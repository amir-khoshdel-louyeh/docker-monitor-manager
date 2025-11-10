## Project Title

**Docker Monitor Manager (DMM)**  
*A Native Desktop Tool for Real-Time Docker Container Monitoring and Management*

**Author:** Amir Khoshdel Louyeh  
**Email:** amirkhoshdellouyeh@gmail.com  
**Repository:** https://github.com/amir-khoshdel-louyeh/docker-monitor-manager  
**License:** MIT  
**Programming Language:** Python 3.8+  
**Primary Framework:** Tkinter (GUI), Docker SDK for Python  
**Project Type:** Desktop Application with CLI Tools Suite

---

## Abstract / Overview

Docker Monitor Manager (DMM) is a sophisticated, lightweight native desktop application developed in Python that provides real-time monitoring, management, and intelligent auto-scaling capabilities for Docker containers. The project addresses the critical need for system administrators, DevOps engineers, and developers to efficiently monitor container resource utilization and perform management operations through an intuitive graphical user interface without relying on web-based solutions or cloud platforms.

#picture: Screenshot of the Docker Monitor Manager main application window showing container list, statistics, and control buttons.

### Problem Statement

Modern containerized environments often suffer from several challenges:

**Resource Monitoring Complexity**: Traditional Docker management relies heavily on command-line interfaces, making real-time resource monitoring cumbersome and inefficient for users who prefer visual interfaces.

**Lack of Native Desktop Solutions**: Most Docker management tools are either web-based (requiring additional infrastructure) or cloud-dependent (raising security and privacy concerns), leaving a gap for lightweight, native desktop applications.

**Manual Scaling Operations**: Container scaling operations typically require manual intervention, leading to delayed responses to resource constraints and potential service degradation.

**Fragmented Tooling**: Docker management often requires using multiple separate tools for monitoring, management, configuration, and troubleshooting, creating workflow inefficiencies.

**Configuration Complexity**: Setting up Docker environments, particularly on Linux systems with AppArmor or SELinux, can be challenging for users unfamiliar with security contexts and permissions.

### Solution Overview

Docker Monitor Manager addresses these challenges by providing:

**Unified Native Application**: A single, lightweight desktop application built with Python's Tkinter framework that runs natively on Linux, Windows, and macOS without requiring web servers or cloud connectivity.

**Real-Time Monitoring**: Live CPU and memory utilization statistics for all running containers, updated continuously and displayed in an intuitive interface.

**Intelligent Auto-Scaling**: Automated detection of resource-constrained containers and intelligent creation of lightweight clones to distribute load, with policy-based management of scaled instances.

**Comprehensive Management Interface**: Full container lifecycle management (start, stop, pause, unpause, restart, remove) directly from the GUI with both individual and batch operations.

**Embedded Secure Terminal**: A restricted terminal widget that allows safe execution of Docker commands from within the application without exposing the system to arbitrary shell command execution.

**Extensive CLI Tools Suite**: Nine specialized command-line utilities for system configuration, health diagnostics, automated updates, testing, cleanup, and complete uninstallation.

**Built-in Documentation**: Comprehensive help system accessible through both GUI and CLI, reducing the learning curve and improving user productivity.

#picture: Screenshot showing the embedded terminal widget executing Docker commands within the application.

### Target Audience

The application is designed for:

- **System Administrators**: Managing multiple Docker containers across development, staging, or production environments
- **DevOps Engineers**: Monitoring container health and performance as part of continuous deployment pipelines
- **Software Developers**: Testing and debugging containerized applications during development
- **Students and Educators**: Learning Docker concepts through visual feedback and experimentation
- **Small to Medium Businesses**: Organizations requiring lightweight container management without enterprise-scale orchestration platforms

### Key Differentiators

**Zero Web Dependencies**: Runs entirely as a native desktop application

**Intelligent Auto-Scaling**: Proactive container cloning based on resource thresholds

**Security-First Design**: Restricted terminal access and safe command execution

**Comprehensive CLI Suite**: Full automation and troubleshooting capabilities

**Cross-Platform Compatibility**: Single codebase supporting Linux, Windows, and macOS

**Minimal Resource Footprint**: Lightweight Python application with minimal dependencies

**Open Source**: MIT licensed, encouraging community contributions and transparency

---

### Features ✨
- 📈 **Live container stats** (CPU%, RAM%)
- ⚡ **Auto-scale** containers when resource limits are exceeded
- ⏯️ **Manage containers**: Stop, Pause, Unpause, Restart, and Remove containers directly from the UI.
- 🎛️ **Global controls**: Apply actions to all containers at once.
- 🖥️ **Embedded Terminal**: A secure terminal for running `docker` commands.
- 📝 **Live Application Logs**: See what the monitor is doing in real-time.
- ⚙️ **Dynamic Configuration**: Adjust CPU/RAM limits and other settings without restarting the app.
- 🔄 **Auto-Update**: Update to the latest version with a single command (`dmm-update`)
- 📚 **Comprehensive Help**: Built-in help system for all CLI tools (`dmm-help`)
- 🏥 **Health Checker**: Automatic diagnosis and fixing of common Docker issues (`dmm-doctor`)
- 🧪 **Test Environment**: Easily create test containers for verification (`dmm-test`)

### Target Achievement Goals

**Functional Goals**

✅ **Real-Time Monitoring**: Achieve sub-3-second update intervals for container statistics  
✅ **Comprehensive Operations**: Support all essential Docker operations (container, image, network, volume management)  
✅ **Security**: Implement restricted command execution to prevent system compromise  
✅ **Reliability**: Maintain stable operation with 50+ concurrent containers  
✅ **Ease of Use**: Enable new users to start monitoring containers within 2 minutes of installation  

**Technical Goals**

✅ **Cross-Platform**: Single codebase running on Linux, Windows, and macOS  
✅ **Minimal Dependencies**: Require only 3 external packages (docker, Pillow, psutil)  
✅ **Low Resource Usage**: Keep memory footprint under 100MB with typical workloads  
✅ **Modular Design**: Enable easy addition of new features without refactoring core components  
✅ **Professional Distribution**: Publish to PyPI with proper versioning and documentation  

**User Experience Goals**

✅ **Intuitive Interface**: Enable users to perform common operations without reading documentation  
✅ **Comprehensive Help**: Provide built-in documentation accessible offline  
✅ **Fast Installation**: Complete installation and setup in under 5 minutes  
✅ **Clear Feedback**: Show immediate visual feedback for all user actions  
✅ **Error Recovery**: Provide actionable guidance when errors occur  

---


## Project Structure

Below is the exact file/directory structure of the repository as it exists in the workspace right now.

```
docker_monitor/
├── __init__.py
├── __pycache__/
├── assets/
│   ├── docker-monitor-manager-128x128.png
│   ├── docker-monitor-manager-16x16.png
│   ├── docker-monitor-manager-256x256.png
│   ├── docker-monitor-manager-32x32.png
│   ├── docker-monitor-manager-48x48.png
│   ├── docker-monitor-manager-512x512.png
│   ├── docker-monitor-manager-64x64.png
│   ├── docker-monitor-manager.svg
│   └── icon.png
├── cli/
│   ├── __init__.py
│   ├── cleanup.py
│   ├── config.py
│   ├── doctor.py
│   ├── help.py
│   ├── setup.py
│   ├── test.py
│   ├── uninstall.py
│   └── update.py
├── gui/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── docker_monitor_app.py
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── container_manager.py
│   │   ├── image_manager.py
│   │   ├── info_display_manager.py
│   │   ├── network_manager.py
│   │   ├── prune_manager.py
│   │   ├── system_manager.py
│   │   └── volume_manager.py
│   └── widgets/
│       ├── __init__.py
│       ├── __pycache__/
│       ├── copy_tooltip.py
│       ├── docker_terminal.py
│       └── ui_components.py
├── main.py
└── utils/
	├── __init__.py
	├── __pycache__/
	├── buffer_handler.py
	├── docker_controller.py
	├── docker_utils.py
	├── observer.py
	├── process_worker.py
	└── worker.py
```


#### CLI Tools Suite (`docker_monitor/cli/`)

Nine specialized command-line tools provide comprehensive system management:

1. **dmm-config** (`config.py`): System configuration and Docker installation helper
2. **dmm-doctor** (`doctor.py`): Comprehensive health diagnostics with guided fixes
3. **dmm-cleanup** (`cleanup.py`): Resource cleanup and orphaned process termination
4. **dmm-test** (`test.py`): Test environment creation with stress containers
5. **dmm-setup** (`setup_tools/post_install.py`): Desktop entry and icon installation
6. **dmm-update** (`update.py`): Automated package updates from PyPI
7. **dmm-help** (`help.py`): Comprehensive documentation and help system
8. **dmm-uninstall** (`uninstall.py`): Complete removal utility with auto-detection
9. **dmm** / **docker-monitor-manager** (`main.py`): GUI application launcher


### All Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `dmm` / `docker-monitor-manager` | Launch the GUI application | `dmm` |
| `dmm-help` | Show help for all commands | `dmm-help` |
| `dmm-help <command>` | Show detailed help for a command | `dmm-help doctor` |
| `dmm-update` | Update to the latest version | `dmm-update` |
| `dmm-setup` | Run post-installation setup | `dmm-setup` |
| `dmm-doctor` | Check system health | `dmm-doctor` |
| `dmm-cleanup` | Prune Docker resources | `dmm-cleanup` |
| `dmm-config` | Configure Docker installation | `dmm-config` |
| `dmm-test` | Create test containers | `dmm-test` |
| `dmm-uninstall` | Uninstall the application | `dmm-uninstall` |

**Quick Command Reference:**
```
dmm-help           # Get help anytime
dmm-update         # Stay up to date
dmm-doctor         # Review diagnostics and suggestions
dmm-cleanup        # Prune unused resources
dmm                # Run the application
```


## How It Works / Workflow

This section summarizes the runtime behavior and data flow of Docker Monitor Manager (DMM): how it collects metrics, reacts to resource pressure with lightweight auto-scaling, executes container/image/network/volume operations, and exposes a restricted embedded terminal and logging for observability.

Monitoring (metrics collection)
- The app polls Docker for live container statistics via the Docker SDK (connects over the Docker socket by default). Key monitored metrics are CPU utilization (calculated from the Docker stats delta formula), memory usage (bytes and percentage), and container state (running, stopped, paused, etc.).
- Default polling frequency is configurable (typical default: every 2 seconds). Polling runs on background worker threads/processes; parsed results are passed to the GUI through thread-safe queues for non-blocking updates.
- Implementation reference: `docker_monitor/utils/docker_controller.py` (`get_container_stats()` and related helpers).

Intelligent auto-scaling (lightweight cloning)
- DMM implements a desktop-oriented auto-scaling policy that triggers when a container breaches configured CPU or memory thresholds (defaults commonly 80%).
- Scaling decision checks: whether a container is marked cloneable, whether a clone exists, and whether host resources permit creating a clone. If the evaluation passes, a clone is created by copying the original container's configuration, assigning a unique name, starting the clone and registering it for lifecycle tracking.
- Clones are tracked via metadata; they are monitored independently and removed according to retention policy or when the original container is removed.

Container operations (individual & batch)
- The GUI and CLI expose full lifecycle operations: start, stop (graceful with configurable timeout), pause/unpause, restart, inspect, remove (with optional `-v` for volumes), and clone (manual or automatic).
- Batch operations are supported (select multiple containers and apply start/stop/restart/remove), with confirmation required for destructive actions.

Image, network and volume management
- Images: list, pull (with progress), remove (safeguarded by checking dependent containers), and inspect (metadata and layer info).
- Networks: list, create (custom subnet/gateway), inspect, and remove unused networks.
- Volumes: list, create, inspect and remove unused volumes. All operations are routed through the Docker Controller and exposed in the GUI manager tabs and CLI tools.

Embedded terminal (security model)
- The embedded terminal exposes Docker CLI functionality while preventing arbitrary system command execution. It enforces a whitelist and blocks shell metacharacters and redirections. Allowed input is restricted to docker commands (and a few safe helpers like `clear`).
- Terminal features include history, basic autocomplete for Docker commands, output formatting, and a scrollback buffer.

### Security notes

- The embedded terminal widget only allows commands that start with `docker` — arbitrary shell commands are rejected by design. The only exception is the `clear` command.
- `dmm-config` may run package-manager commands with `sudo` when requested by the user. It is intentionally conservative and prompts before making changes.

Application logging & observability
- All subsystems log through a centralized logging setup. `buffer_handler.py` implements a thread-safe circular buffer that the GUI reads to display real-time logs.
- Logs are timestamped and filterable by level. The buffer supports export for offline troubleshooting.

Data flow summary (input → processing → output)
- Input: Docker API (container lists, stats, inspect), user actions from GUI, and CLI commands.
- Processing: background workers poll and parse metrics, managers apply business logic (auto-scale, pruning, container actions), and the Docker Controller executes API calls.
- Output: live GUI updates (charts, tables, logs), CLI textual outputs, created/removed containers/images/networks/volumes, and desktop integration side-effects (icons/desktop entries).

## Algorithms & Logic

This project applies practical, lightweight algorithms focused on monitoring, decision-making for auto-scaling, and safe orchestration of Docker operations. Key points:

- Metrics calculation: CPU% computed from Docker stats deltas using the standard formula (container_cpu_delta / system_cpu_delta * cpus * 100); memory% as used/available * 100. Sampling and smoothing reduce metric noise.
- Auto-scaling: threshold-based triggers (CPU/memory) followed by eligibility checks (cloneable label, existing clones, host resources) and clone creation that replicates container configuration. Clones are tracked and garbage-collected per policy.
- Observer and workers: observer pattern notifies listeners of container lifecycle events; background worker threads/processes poll Docker and push updates to the GUI via thread-safe queues.
- Safety: transient errors are retried with backoff; permanent errors surface to users. Destructive operations require confirmations and support dry-run where useful.
- Contracts: CLI tools return clear exit codes; GUI mirrors CLI operations with additional confirmations and progress UI.

These algorithms are implemented across `docker_monitor/utils/docker_controller.py`, `docker_monitor/gui/managers/`, and `docker_monitor/utils/worker.py`.

See `docker_monitor/gui/`, `docker_monitor/utils/`, and `docker_monitor/cli/` for concrete implementations and function-level details.

## Troubleshooting (common)

- **"permission denied" when accessing Docker:**
	- Run `dmm-doctor` to diagnose the issue and follow the suggested steps.
	- Or manually: Ensure the Docker daemon is running: `sudo systemctl start docker` (or use your distro's service manager).
	- Add your user to the `docker` group and re-login: `sudo usermod -aG docker $USER` then logout/login or `newgrp docker`.
	- If AppArmor is interfering, use `dmm-config` to inspect and optionally change the Docker AppArmor profile.

- **Application not working correctly:**
	- Run `dmm-doctor` to check for common issues.
	- Run `dmm-test` to create test containers and verify functionality.

- **Want to update to the latest version:**
	- Simply run `dmm-update` to download and install the latest version from PyPI.


## How to Run / Installation Guide
I inspected `docker_monitor/main.py` and `README.md` to ensure accurate instructions. The project expects Python 3.8+ and Docker Engine.

Minimal steps (local install & run):

1. Prerequisites
	 - Python 3.8+ installed
	 - Docker Engine installed and running
	 - On Linux, optionally add your user to the `docker` group to avoid `sudo`:
		 ```bash
		 sudo usermod -aG docker $USER
		 # then log out/in or run:
		 newgrp docker
		 ```

2. Install (from source)
	 ```bash
	 git clone https://github.com/amir-khoshdel-louyeh/docker-monitor-manager.git
	 cd docker-monitor-manager
	 pip install .
	 ```

	 Alternatively, if published, install from PyPI:
	 ```bash
	 pip install docker-monitor-manager
	 ```

	 Or with pipx:
	 ```bash
	 pipx install docker-monitor-manager
	 ```

3. Run post-install setup
	 - After installation, run the setup helper to create desktop entry and icons:
	 ```bash
	 dmm-setup
	 ```

4. Start the GUI
	 - Run via the console entry point:
	 ```bash
	 docker-monitor-manager
	 # or
	 dmm
	 ```
	 - Or run directly with Python for development:
	 ```bash
	 python -m docker_monitor.main
	 ```

5. Use CLI tools
	 - Help:
	 ```bash
	 dmm-help
	 dmm-help doctor
	 ```
	 - Update:
	 ```bash
	 dmm-update
	 ```
	 - Health check and auto-fixes:
	 ```bash
	 dmm-doctor
	 ```
	 - Cleanup:
	 ```bash
	 dmm-cleanup
	 ```
	 - Create test containers:
	 ```bash
	 dmm-test
	 ```

Dependencies
- The `requirements.txt` lists core runtime dependencies:
	- `docker`
	- `Pillow>=9.0.0`
	- `psutil>=5.9.0`

Development & quick checks
- Syntax / import quick tests shown in `README.md`:
	```bash
	python3 -m py_compile docker_monitor/*.py
	python3 -c "import docker_monitor.main as m; print('OK')"
	```
- Build a distribution:
	```bash
	pip install build
	python -m build
	```

### Packaging & platform notes

- Windows: the GUI attempts to use generated `.ico` if available (requires Pillow to generate icons).
- macOS: packaging as a `.app` (py2app) is recommended for a native experience and to generate `.icns` correctly.
- Linux: Tkinter `PhotoImage` PNGs usually work for in-window icons.


## Conclusion
Docker Monitor Manager provides a compact but feature-rich desktop environment and CLI toolset to monitor Docker containers, perform maintenance, and assist in troubleshooting Docker-related issues on developer machines. The project organizes core concerns clearly:
- GUI responsibilities and widgets under `docker_monitor/gui/`
- Management logic under `docker_monitor/gui/managers/`
- CLI tools under `docker_monitor/cli/`
- Utility concerns (logging buffering, Docker wrapper, observers and workers) under `docker_monitor/utils/`

What was accomplished in this report:
- Identified the project name and primary purpose.
- Summarized how the project runs (entrypoints and background processes).
- Documented the repository structure and key files to look at for each major behavior.
- Outlined the main algorithms and policies used (monitoring, auto-scaling, pruning, health checks).
- Provided accurate installation and run instructions verified from `README.md` and `docker_monitor/main.py`, and listed dependencies from `requirements.txt`.

If you'd like, I can:
- Produce a one-page PDF of this report.
- Create a short "developer quick start" script (Makefile or small shell script) with commands to set up a dev environment and run the GUI.
- Add or update tests for a couple of core utils (e.g., unit tests for `docker_utils.py` behaviors).
