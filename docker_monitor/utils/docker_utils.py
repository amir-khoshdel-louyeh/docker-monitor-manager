import docker
import time
import logging
import queue
import threading
import uuid

# Import the Docker Data Controller
from docker_monitor.utils.docker_controller import get_docker_controller

# --- Configuration ---
CPU_LIMIT = 50.0  # %
RAM_LIMIT = 5.0   # %
CLONE_NUM = 2     # Max clones per container
SLEEP_TIME = 1    # Polling interval in seconds
# Feature flags / policies
# By default disable automatic scaling to avoid unexpected container creation
# unless explicitly enabled by the user in settings/UI.
AUTO_SCALE_ENABLED = True
# Configuration version: increment when any runtime config value changes.
# Monitor loop checks this to avoid acting on stale decisions when the
# configuration is updated concurrently from the GUI.
CONFIG_VERSION = 0

# Only react to events for containers that the app created (label) or that
# match this name prefix. This prevents the GUI from chasing external
# test harness containers unless you opt in.
APP_CONTAINER_NAME_PREFIX = 'dmm-'
APP_CREATED_BY_LABEL = 'docker-monitor-manager'

# --- Docker Client and Logic ---
try:
    client = docker.from_env()
    client.ping()
    logging.info("Docker client connected successfully!")
except Exception as e:
    logging.error(f"Docker client failed to connect: {e}")
    exit(1)


# Queues for inter-thread communication
stats_queue = queue.Queue(maxsize=5)
manual_refresh_queue = queue.Queue()  # A dedicated queue for manual refresh results
network_refresh_queue = queue.Queue(maxsize=5)
logs_stream_queue = queue.Queue(maxsize=20)
events_queue = queue.Queue(maxsize=50)
docker_lock = threading.Lock()  # A lock to prevent race conditions on Docker operations


def _offer_latest(q: queue.Queue, item, queue_name: str) -> None:
    """Drop oldest entry when the bounded queue is full and enqueue the latest snapshot."""
    try:
        q.put_nowait(item)
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        try:
            q.put_nowait(item)
        except queue.Full:
            logging.debug(f"{queue_name} queue saturated; dropping update")


def calculate_cpu_percent(stats):
    """Calculate CPU usage percentage from Docker stats."""
    try:
        cpu_current = stats['cpu_stats']['cpu_usage']['total_usage']
        cpu_prev = stats['precpu_stats']['cpu_usage']['total_usage']
       
        system_current = stats['cpu_stats']['system_cpu_usage']
        system_prev = stats['precpu_stats']['system_cpu_usage']

        cpu_delta = cpu_current - cpu_prev
        system_delta = system_current - system_prev

        num_cpus = stats['cpu_stats'].get('online_cpus', 1)
        
        if system_delta > 0 and cpu_delta > 0:
            CPU_percent = (cpu_delta / system_delta) * num_cpus * 100.0
        else:
            CPU_percent = 0.0

        return CPU_percent
    except (KeyError, TypeError):
        pass
    return 0.0


def calculate_ram_percent(stats):
    """Calculate RAM usage percentage from Docker stats."""
    try:
        mem_usage = stats['memory_stats'].get('usage', 0)
        mem_limit = stats['memory_stats'].get('limit', 1)
        return (mem_usage / mem_limit) * 100.0
    except (KeyError, TypeError):
        pass
    return 0.0


def get_container_stats(container):
    """Get stats for a single container with timeout protection."""
    if container is None:
        logging.warning("get_container_stats called with None container")
        return {
            'id': 'unknown', 
            'name': 'unknown', 
            'status': 'error', 
            'cpu': '0.00', 
            'ram': '0.00'
        }
    
    try:
        # Only fetch stats for running containers to improve performance
        # For stopped containers, just return basic info
        if container.status != 'running':
            return {
                'id': container.short_id,
                'name': container.name,
                'status': container.status,
                'cpu': '0.00',
                'ram': '0.00'
            }
        
        # Fetch stats with a timeout to prevent hanging
        # Use stream=False for non-blocking single stat fetch
        stats = container.stats(stream=False)

        cpu = calculate_cpu_percent(stats)
        ram = calculate_ram_percent(stats)
        return {
            'id': container.short_id,
            'name': container.name,
            'status': container.status,
            'cpu': f"{cpu:.2f}",
            'ram': f"{ram:.2f}"
        }
    except docker.errors.NotFound:
        # Container was removed while we were fetching stats
        logging.debug(f"Container {getattr(container, 'name', 'unknown')} not found (likely removed)")
        return None
    except Exception as e:
        logging.debug(f"Error getting stats for container {getattr(container, 'name', 'unknown')}: {e}")
        # Return basic info instead of erroring out
        try:
            return {
                'id': container.short_id,
                'name': container.name,
                'status': container.status,
                'cpu': '0.00',
                'ram': '0.00'
            }
        except:
            return {
                'id': 'unknown', 
                'name': 'unknown', 
                'status': 'error', 
                'cpu': '0.00', 
                'ram': '0.00'
            }


def is_clone_container(container):
    """
    Check if a container is a clone created by this application.
    Uses labels to identify clone containers reliably.
    """
    if container is None:
        return False
    
    try:
        labels = container.labels or {}
        return labels.get('dmm.is_clone') == 'true' and 'dmm.parent_container' in labels
    except (AttributeError, TypeError) as e:
        logging.debug(f"Error checking if container is clone: {e}")
        return False


def get_parent_container_name(container):
    """Get the parent container name from a clone container."""
    if container is None:
        return ''
    
    try:
        labels = container.labels or {}
        return labels.get('dmm.parent_container', '')
    except (AttributeError, TypeError) as e:
        logging.debug(f"Error getting parent container name: {e}")
        return ''


def delete_clones(container, all_containers):
    """Delete all clone containers for a given container."""
    if container is None or all_containers is None:
        logging.warning("delete_clones called with None parameter")
        return
    
    try:
        container_name = container.name
    except AttributeError:
        logging.error("Container object has no 'name' attribute")
        return
    
    # Use list comprehension to filter clones - faster than manual loop
    existing_clones = [c for c in all_containers if is_clone_container(c) and get_parent_container_name(c) == container_name]
    
    # Define deletion function once to avoid repeated try-catch overhead
    def delete_clone(clone):
        try:
            clone.stop(timeout=10)
            clone.remove()
            logging.info(f"Deleted clone container {clone.name}.")
        except docker.errors.NotFound:
            logging.debug(f"Clone container {getattr(clone, 'name', 'unknown')} already removed")
        except Exception as e:
            logging.error(f"Failed to delete clone container {getattr(clone, 'name', 'unknown')}: {e}")
    
    # Apply deletion using map (avoids explicit loop)
    list(map(delete_clone, existing_clones))


def docker_cleanup():
    """Cleanup Docker resources."""
    try:
        # Use the Docker SDK for a cleaner and more robust implementation
        # Prune stopped containers, dangling images, unused volumes and networks
        try:
            containers_result = client.containers.prune()
            logging.info(f"Pruned containers: {containers_result.get('ContainersDeleted')}")
        except Exception:
            logging.debug("No stopped containers to prune or prune failed")

        try:
            images_result = client.images.prune(filters={'dangling': True})  # Prune dangling images
            logging.info(f"Pruned images: {images_result.get('ImagesDeleted')}, reclaimed={images_result.get('SpaceReclaimed')}")
        except Exception:
            logging.debug("Image prune failed")

        try:
            volumes_result = client.volumes.prune()
            logging.info(f"Pruned volumes: {volumes_result.get('VolumesDeleted')}")
        except Exception:
            logging.debug("Volume prune failed")

        try:
            networks_result = client.networks.prune()
            logging.info(f"Pruned networks: {networks_result.get('NetworksDeleted')}")
        except Exception:
            logging.debug("Network prune failed")
    except Exception as e:
        logging.error(f"An error occurred during Docker cleanup: {e}")


def scale_container(container, all_containers):
    """Scale a container by creating clones."""
    if container is None or all_containers is None:
        logging.warning("scale_container called with None parameter")
        return
    
    try:
        container_name = container.name
    except AttributeError:
        logging.error("Container object has no 'name' attribute")
        return
    
    existing_clones = [c for c in all_containers if is_clone_container(c) and get_parent_container_name(c) == container_name]

    if len(existing_clones) >= CLONE_NUM:
        logging.info(f"Max clones reached for '{container_name}'. Pausing original and deleting clones.")
        try:
            container.pause()
            logging.info(f"Paused original container '{container_name}'.")
        except docker.errors.APIError as e:
            logging.error(f"Failed to pause original container '{container_name}': {e}")
        except Exception as e:
            logging.error(f"Unexpected error pausing container '{container_name}': {e}")
        delete_clones(container, all_containers)
    # Do NOT schedule automatic cleanup here. Resource pruning should only
    # be performed when the user explicitly requests it via the UI prune
    # buttons. This avoids unexpected image/volume/network pruning during
    # scaling operations.
        return

    # If auto-scaling is disabled, do not create clones automatically.
    if not AUTO_SCALE_ENABLED:
        logging.info(f"Auto-scaling is disabled; skipping clone creation for '{container_name}'")
        return

    # Automatic clone creation: create a labeled clone of the container.
    # Safety notes:
    #  - Do not exceed CLONE_NUM total clones for a given parent.
    #  - Create at most one clone per scale event to avoid bursts.
    #  - Label clones so they can be identified and deleted by `delete_clones`.
    try:
        clones_to_create = max(0, CLONE_NUM - len(existing_clones))
        if clones_to_create <= 0:
            logging.info(f"No clones needed for '{container_name}' (already at max).")
            return

        # Determine the image to use for the clone. Prefer a tagged image when
        # available, fall back to image id.
        image = None
        try:
            if getattr(container, 'image', None) and getattr(container.image, 'tags', None):
                image = container.image.tags[0]
            else:
                image = container.image.id
        except Exception:
            image = getattr(container.image, 'id', None) if getattr(container, 'image', None) else None

        # Try to reuse container command/config where reasonable
        cmd = None
        try:
            cmd = container.attrs.get('Config', {}).get('Cmd') if hasattr(container, 'attrs') else None
        except Exception:
            cmd = None

        labels = {
            'dmm.is_clone': 'true',
            'dmm.parent_container': container_name,
            'dmm.created_by': APP_CREATED_BY_LABEL,
        }

        # Create only one clone per scale invocation for safety. If you want
        # more aggressive scaling, adjust this logic and add rate limiting.
        try:
            clone_name = f"{container_name}-clone-{uuid.uuid4().hex[:8]}"
            new_container = client.containers.run(
                image=image,
                command=cmd,
                name=clone_name,
                detach=True,
                labels=labels,
            )
            logging.info(f"Created clone container '{getattr(new_container, 'name', 'unknown')}' for parent '{container_name}'.")
        except docker.errors.APIError as e:
            logging.error(f"Docker API error creating clone for '{container_name}': {e}")
        except Exception as e:
            logging.error(f"Failed to create clone for '{container_name}': {e}")

    except Exception as e:
        logging.error(f"Unexpected error during clone creation for '{container_name}': {e}")


def monitor_thread():
    """Background thread for monitoring Docker containers."""
    global SLEEP_TIME
    
    # Get the Docker controller instance
    controller = get_docker_controller()

    while True:
        try:
            with docker_lock:
                all_containers = client.containers.list(all=True)

            container_stats_pairs = []
            stats_payload = []
            for container in all_containers:
                stats = get_container_stats(container)
                container_stats_pairs.append((container, stats))
                if stats is not None:
                    stats_payload.append(stats)

            # --- Auto-scaling logic ---
            if AUTO_SCALE_ENABLED:
                # Capture the config version observed at the start of the
                # decision window. If the GUI updates configuration while
                # we are processing, we'll skip acting on stale decisions.
                try:
                    observed_config_version = CONFIG_VERSION
                except NameError:
                    observed_config_version = 0
                running_overloaded = []
                for container, stats in container_stats_pairs:
                    if not stats:
                        continue
                    if container.status != 'running' or is_clone_container(container):
                        continue
                    try:
                        cpu_val = float(stats.get('cpu', 0.0))
                        ram_val = float(stats.get('ram', 0.0))
                    except (TypeError, ValueError):
                        continue
                    if cpu_val > CPU_LIMIT or ram_val > RAM_LIMIT:
                        running_overloaded.append((container, stats))

                for container, stats in running_overloaded:
                    try:
                        # Re-check AUTO_SCALE_ENABLED in case the user toggled
                        # it off after we collected the overloaded list.
                        if not AUTO_SCALE_ENABLED:
                            logging.info(f"Auto-scaling disabled during handling; skipping scaling for '{container.name}'")
                            continue

                        logging.info(
                            "Container %s overloaded (CPU: %s%%, RAM: %s%%). Scaling...",
                            container.name,
                            stats.get('cpu', 'n/a'),
                            stats.get('ram', 'n/a')
                        )

                        # If configuration changed while we were preparing to
                        # act, skip this scaling action to avoid following a
                        # stale decision.
                        try:
                            current_version = CONFIG_VERSION
                        except NameError:
                            current_version = 0

                        if current_version != observed_config_version:
                            logging.info(f"Configuration changed during handling; skipping scaling for '{container.name}'")
                            continue

                        scale_container(container, all_containers)
                    except (ValueError, KeyError, AttributeError) as e:
                        logging.debug(f"Error processing stats for {container.name}: {e}")

            # Notify controller with updated container data (Observer pattern)
            controller.update_containers(stats_payload)

            # Also put in queue for backward compatibility during transition
            _offer_latest(stats_queue, stats_payload, "stats")

        except Exception as e:
            logging.error(f"Error in monitor loop: {e}")
        
        time.sleep(SLEEP_TIME)


def docker_events_listener():
    """
    Background thread that listens to Docker events in real-time.
    Triggers immediate updates when containers are created, started, stopped, or removed.
    """
    logging.info("Docker events listener started")
    
    # Get the Docker controller instance
    controller = get_docker_controller()
    
    # Events we care about for immediate UI updates
    relevant_events = ['create', 'start', 'stop', 'die', 'destroy', 'pause', 'unpause', 'kill', 'restart']
    
    # Debounce rapid events to prevent overwhelming the system
    last_refresh_time = 0
    MIN_REFRESH_INTERVAL = 0.5  # Minimum 500ms between refreshes
    
    try:
        for event in client.events(decode=True):
            try:
                # Only process container events and only the actions we care about
                if event.get('Type') != 'container' or event.get('Action') not in relevant_events:
                    continue

                event_action = event.get('Action')
                attrs = event.get('Actor', {}).get('Attributes', {}) or {}
                container_name = attrs.get('name', 'unknown')

                # Determine whether this container was created by this app
                created_by = attrs.get('dmm.created_by')
                is_app_container = (created_by == APP_CREATED_BY_LABEL) or (
                    isinstance(container_name, str) and container_name.startswith(APP_CONTAINER_NAME_PREFIX)
                )

                if not is_app_container:
                    # External containers: keep noise at DEBUG level and ignore their
                    # events to avoid triggering immediate GUI updates or destructive
                    # reactions.
                    logging.debug(f"External Docker event ignored: {event_action} on '{container_name}'")
                    continue

                logging.info(f"Docker event detected: {event_action} on container '{container_name}'")
                
                # Notify controller about the Docker event (Observer pattern)
                controller.notify_docker_event(event)

                # Debounce: Only refresh if enough time has passed since last refresh
                current_time = time.time()
                if current_time - last_refresh_time < MIN_REFRESH_INTERVAL:
                    logging.debug(f"Skipping refresh due to debounce (last refresh {current_time - last_refresh_time:.2f}s ago)")
                    continue
                
                last_refresh_time = current_time

                # For some rapid create/start/destroy sequences the SDK may return
                # a NotFound when trying to inspect a container that already went
                # away. To reduce noisy 404 logs and avoid transient race errors,
                # sleep a tiny amount for create/start events before listing.
                if event_action in ('create', 'start'):
                    # short debounce to let the container settle
                    time.sleep(0.1)

                # Trigger an immediate refresh by fetching current stats for app containers only
                # Use a timeout to prevent hanging
                def _fetch_and_notify():
                    with docker_lock:
                        try:
                            all_containers = client.containers.list(all=True)
                            
                            # Use list comprehension with error handling - much faster than loop
                            def safe_get_stats(c):
                                try:
                                    return get_container_stats(c)
                                except docker.errors.NotFound:
                                    logging.debug(f"Container disappeared before stats could be read: {getattr(c, 'name', 'unknown')}")
                                    return None
                                except Exception as e:
                                    logging.debug(f"Error getting stats for {getattr(c, 'name', 'unknown')}: {e}")
                                    return None
                            
                            stats_list = [s for s in (safe_get_stats(c) for c in all_containers) if s is not None]

                            # Notify controller with updated container data (Observer pattern)
                            controller.update_containers(stats_list)
                            
                            # Also put in queue for backward compatibility
                            _offer_latest(stats_queue, stats_list, "stats")
                            _offer_latest(manual_refresh_queue, stats_list, "manual refresh")

                            # If the container was destroyed, do NOT run automatic cleanup.
                            # Cleanup/prune should be triggered explicitly by the user.

                        except docker.errors.NotFound as e:
                            # This can happen if a specific container referenced in the
                            # SDK query was removed concurrently. Treat as debug-worthy
                            # rather than an error to avoid alarming logs for races.
                            logging.debug(f"NotFound while processing event {event_action}: {e}")
                        except Exception as e:
                            logging.error(f"Error processing event {event_action}: {e}")
                
                # Execute fetch in a separate thread to avoid blocking the event stream
                from docker_monitor.utils.worker import run_in_thread
                run_in_thread(_fetch_and_notify, on_done=None, on_error=lambda e: logging.error(f"Event refresh failed: {e}"), tk_root=None, block=False)

            except Exception as e:
                logging.error(f"Error handling event: {e}")

    except Exception as e:
        logging.error(f"Docker events listener error: {e}")
        # Avoid infinite recursion - limit restart attempts
        if not hasattr(docker_events_listener, '_restart_count'):
            docker_events_listener._restart_count = 0
        
        docker_events_listener._restart_count += 1
        max_restarts = 5
        
        if docker_events_listener._restart_count < max_restarts:
            # Restart the listener after a short delay
            time.sleep(5)
            logging.info(f"Restarting Docker events listener (attempt {docker_events_listener._restart_count}/{max_restarts})...")
            docker_events_listener()
        else:
            logging.critical(f"Docker events listener failed {max_restarts} times. Stopping automatic restarts.")
            logging.critical("Please check Docker daemon status and restart the application.")
