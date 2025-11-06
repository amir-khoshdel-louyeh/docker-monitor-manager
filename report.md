# Docker Monitor Manager — Project Report

## General information

Repository: docker-monitor-manager

Purpose: Docker Monitor Manager is a small native desktop application and set of CLI utilities for monitoring and managing Docker containers. It provides a Tkinter-based GUI for live container statistics, basic management actions (stop/pause/restart/remove), an embedded restricted terminal for running docker commands, auto-scaling behavior (lightweight clones for overloaded containers), logging, and a suite of CLI helpers for system configuration, health checks, test environments, installation/setup, updates and uninstallation.

Language & platform: Python (3.8+). The GUI uses Tkinter. The project targets Linux, macOS and Windows with platform-specific packaging notes included in the repository.

Key runtime dependencies: docker (Python SDK), psutil (system metrics), Pillow (icon generation). See `requirements.txt` and `pyproject.toml` for full dependency pins.

## Project structure and file concepts

This section summarizes the repository layout, where to find key functionality, and how components interact at a high level. The layout follows a conventional Python package structure with additional helper scripts for packaging and desktop integration.

**Top-level files**
- `README.md` — User-facing documentation, usage examples, and command reference (summarized in this report).
- `setup.py`, `pyproject.toml`, `requirements.txt` — Packaging and dependency metadata.
- `report.md` — This report (project overview and usage summary).

**Main package (`docker_monitor/`)**
- `__init__.py` — Package metadata (version, author).
- `main.py` — Application entry point for the GUI; also used for the console entry point when installed (`docker-monitor-manager` / `dmm`).

**CLI tools (`docker_monitor/cli/`)**
- `config.py` — `dmm-config` helper to detect / configure Docker and optional AppArmor/SELinux adjustments.
- `doctor.py` — `dmm-doctor` health checker with guided fixes.
- `cleanup.py` — `dmm-cleanup` maintenance utility that prunes unused Docker resources and frees orphaned container memory.
- `help.py` — `dmm-help` — displays documentation and usage for the CLI tools.
- `setup.py` — `dmm-setup` — post-installation setup (desktop entry and icons).
- `test.py` — `dmm-test` — test environment creator (creates containers used to verify monitoring).
- `update.py` — `dmm-update` — auto-update helper that pulls latest from PyPI and runs setup.
- `uninstall.py` — `dmm-uninstall` — complete uninstaller that removes installed files and desktop entries.

**GUI (`docker_monitor/gui/`)**
- `docker_monitor_app.py` — The Tkinter application bootstrap and main window.
- `managers/` — A collection of managers handling different responsibilities in the UI:
  - `container_manager.py` — Listing containers, actions (stop, pause, restart, remove), clone management, and live stats.
  - `image_manager.py`, `network_manager.py`, `volume_manager.py`, `system_manager.py`, `prune_manager.py` — Supporting management screens and actions.
  - `info_display_manager.py` — Manages the information panels and logs.
- `widgets/` — Reusable UI widgets used in the app (embedded terminal, tooltips, common UI components).

**Utilities (`docker_monitor/utils/`)**
- `docker_utils.py` — Thin wrappers around the Docker Python SDK used by the GUI and CLI tools.
- `buffer_handler.py` — Utilities for handling streaming logs and buffers used in the app.
- `worker.py`, `process_worker.py` — Thread- and process-based executors that keep blocking Docker work off the Tk event loop.
- `observer.py` — Observer pattern primitives used to broadcast UI/data updates safely across threads.

**Setup tools (`setup_tools/`)**
- Scripts and helper files for packaging, desktop entries, icons and post-install actions.

**Tests (`tests/`)** — Test utilities and test cases (if present). These provide basic compile/import checks and test container lifecycle tests via `dmm-test`.

**Other supporting files and assets**
- `MANIFEST.in`, `LICENSE`, `README.md` — Packaging and documentation artifacts for distribution.
- `docker_monitor/assets/` — Icon and image assets bundled with the GUI (status indicators, tray icons, etc.).
- `setup_tools/icons/` — Source icon set consumed by the desktop integration scripts.

How components interact (concise):

- The GUI (`docker_monitor_app.py`) composes managers and widgets. Managers call into `docker_utils.py` to query container lists, fetch stats and execute Docker operations. `buffer_handler.py` is used when streaming logs or piping command output into the embedded terminal widget.
- CLI helpers reuse `docker_utils.py` and shared helpers so the same logic is available to headless users and automated scripts. This avoids duplication between the GUI and CLI.
- `setup_tools/` is only used during packaging and the `dmm-setup` step; its scripts produce icons and desktop entries so the GUI can be launched from the desktop environment.

Where to make common changes

- To change container metrics or sampling frequency: edit the container manager implementation in `docker_monitor/gui/managers/container_manager.py`.
- To alter cloning/auto-scaling policy: find the scaling logic in the container manager and the Docker helper functions in `docker_monitor/utils/docker_utils.py` that create/manage clones.
- To add or modify CLI behavior: edit the corresponding module in `docker_monitor/cli/` and update entry point mappings in `setup.py` or `pyproject.toml`.

These notes are intended as a quick orientation for developers and maintainers. For code-level navigation, search for names like `container_manager`, `docker_utils` and `docker_monitor_app` which are central integration points.

## What this project does (summary)

This project provides both a graphical desktop application and a set of command-line utilities for monitoring and managing Docker resources with a focus on simplicity and safety. Key capabilities include:

- Live container monitoring: The GUI displays per-container resource metrics such as CPU percentage, memory usage, and basic I/O statistics. Metrics are updated at a short interval to give the user near-real-time visibility into container behavior without requiring external monitoring stacks.

- Lightweight auto-scaling: When a container exceeds configured resource thresholds, the application can automatically create lightweight clones of that container to share load. Clone lifecycle is managed by a simple policy (scale-up when overloaded, scale-down when underutilized) to avoid runaway resource consumption. Cloning is intended for short-lived relief and testing, not as a production replacement for orchestrators.

- In-app container management: From the UI users can perform common actions such as stop, pause, unpause, restart and remove. These actions are performed through the Docker Python SDK and are presented with confirmation dialogs to reduce accidental destructive operations.

- Restricted embedded terminal: A terminal widget embedded in the GUI accepts only a limited set of safe commands (those that begin with `docker` and the `clear` command). This minimizes the risk of arbitrary command execution while enabling power users to run container commands from within the app.

- Live application logs: The app surfaces its internal logs and recent Docker events in an integrated log view. This helps with troubleshooting and understanding recent actions (for example, scale events or failed API calls).

- CLI helper utilities: A suite of small command-line programs (prefixed with `dmm-`) support installation/post-install setup, health checks, automated fixes for common issues, test environment creation (for validating monitoring features), updates, and uninstallation. These tools let advanced users script and automate common maintenance tasks.

## How to install

The project supports several common installation methods so you can choose between a system-wide library install, an isolated CLI install, or a developer/source installation. All methods have the same runtime prerequisites (Python 3.8+, and a running Docker Engine).

1) Install from PyPI (stable release):
	- This is the simplest method for end users. It installs the package and exposes the CLI entry points.
	- Example: `pip install docker-monitor-manager`

2) Install with pipx (recommended for isolated CLI installs):
	- `pipx` creates a per-application virtual environment and puts the CLI into your PATH without touching your system Python packages.
	- Example: `pipx install docker-monitor-manager`

3) Install from source (developer / local install):
	- Useful if you want to modify the code or use the latest master branch.
	- Example:
	  - `git clone <repo>`
	  - `cd docker-monitor-manager`
	  - `pip install .`
Post-install step (desktop integration):
- Run `dmm-setup` after installation to create the desktop entry and install icons so the GUI appears in your desktop environment's application menu. On Linux this writes a `.desktop` file to the user's applications directory.

Runtime prerequisites and notes:
- Python 3.8 or newer.
- Docker Engine must be installed and running (daemon active).
- On Linux, to allow non-root Docker access: `sudo usermod -aG docker $USER` and then re-login or run `newgrp docker`.
- The application depends on the Python `docker` package (Docker SDK), `psutil` for cleanup/metrics, and optionally `Pillow` for icon manipulation. Exact pinned versions are in `requirements.txt` and `pyproject.toml`.

## How to run

GUI
- After installation and running `dmm-setup`, launch the GUI with one of the installed entry points: `docker-monitor-manager` or the shorter alias `dmm`. If you installed the desktop entry, you can also use the desktop menu item named "Docker Monitor Manager" to start the app.

- The GUI is a single-window Tkinter application that lists containers, metrics, and management actions. The embedded terminal and logging panel are available from the main window.

CLI utilities
- The package provides several small CLI helper programs. Each is designed to be simple and scriptable:
	- `dmm-help`: Prints usage and examples for all CLI helpers and commonly used GUI workflows.
  - `dmm-update`: Pulls the latest release from PyPI (if available) and runs post-install setup automatically.
  - `dmm-doctor`: Runs a set of diagnostic checks against the Docker environment and suggests conservative fixes.
  - `dmm-cleanup`: Prunes stopped containers, dangling images, unused networks/volumes, and clears orphaned containerd shim processes to reclaim memory.
  - `dmm-config`: System configuration helper that inspects policies like AppArmor/SELinux and performs required changes automatically.
  - `dmm-test`: Creates simple test containers used to verify monitoring, cloning, and resource reporting. Supports `status` and `cleanup` subcommands for inspecting or removing test containers.
	- `dmm-setup`: Performs post-install desktop integration (desktop entry, icons, optional application shortcuts).
	- `dmm-uninstall`: Removes installed files and desktop entries created by `dmm-setup`.

Quick start (recommended):
1. `pip install docker-monitor-manager` (or use `pipx install docker-monitor-manager`)
2. `dmm-setup`
3. `dmm-doctor` (review diagnostics and follow the suggestions)
4. `dmm-cleanup` (reclaim disk/memory resources on the host)
5. (optional) `dmm-test` to create sample containers
6. `dmm` or open the app from your desktop menu

## Operational workflow

1. **Verify prerequisites**: Ensure Docker Engine is installed and running; add the target user to the `docker` group so CLI and GUI actions can reach the socket without root.
2. **Install the toolkit**: Choose PyPI, `pipx`, or source installation depending on whether you need isolation, system-wide availability, or editable code.
3. **Integrate with the desktop**: Run `dmm-setup` to create menu entries and stage icons from `setup_tools/` so the GUI is discoverable in standard launchers.
4. **Diagnose the host**: Execute `dmm-doctor` to validate daemon health, permissions, networking, and resource sufficiency. Follow emitted guidance when warnings appear.
5. **Reclaim resources**: Run `dmm-cleanup` to prune unused Docker artifacts and terminate orphaned `containerd-shim` processes before launching production workloads.
6. **Stage test fixtures (optional)**: Use `dmm-test` to create disposable containers that exercise monitoring, cloning, and teardown paths without touching live services.
7. **Operate via the GUI**: Launch `dmm`/`docker-monitor-manager`, connect to the Docker host, and manage containers through the managers, widgets, and embedded terminal.
8. **Adjust system policies**: If AppArmor/SELinux or package-level prerequisites are missing, leverage `dmm-config` to apply the recommended policy changes.
9. **Maintain and update**: Periodically run `dmm-update` to pull the latest release and re-run `dmm-setup`; invoke `dmm-uninstall` when removing the toolkit.

## README.md highlights

The README begins with a feature tour of the GUI: real-time metrics, inline lifecycle actions, clone labelling, the restricted terminal, and live logs. Each capability is paired with screenshots or callouts so operators can match what they see on screen with the documented workflow.

Installation guidance is comprehensive, covering PyPI, `pipx`, and source setups. The document stresses running `dmm-setup` immediately after installation to register desktop entries and icons, and it calls out when administrator privileges or group membership changes are required (for example, adding a user to the `docker` group on Linux).

Subsequent sections act as a command reference. Every helper prefixed with `dmm-` has usage examples, exit behavior, and notes on side effects. The README recommends an end-to-end sequence—install, integrate (`dmm-setup`), diagnose (`dmm-doctor`), reclaim resources (`dmm-cleanup`), optionally stage demo containers (`dmm-test`), then launch the GUI.

Troubleshooting material addresses Docker daemon availability, socket permissions, SELinux/AppArmor policy conflicts, and techniques for gathering diagnostics. Readers are directed to run `dmm-doctor`, consult the GUI log pane, and verify group membership before escalating issues.

For contributors, the README closes with developer notes: quick syntax/import smoke tests, release build instructions (`python -m build`), and a condensed map of the source tree so new maintainers can find entry points rapidly.

## Code reference — key modules

- **CLI helpers (`docker_monitor/cli/`)**
	- `cleanup.py`: Implements `dmm-cleanup`, issuing safe `docker * prune --force` commands and terminating orphaned `containerd-shim` workers via `psutil` to reclaim RAM.
	- `doctor.py`: Runs environment diagnostics only; prints guidance and defers cleanup to `dmm-cleanup`.
	- `config.py`, `setup.py`, `update.py`, `uninstall.py`: Automate environment setup, desktop integration, upgrades, and removal flows.
	- `test.py`: Creates and cleans sample containers so users can validate monitoring without touching production workloads.
	- `help.py`: Renders consolidated documentation and per-command examples for all helpers.

- **GUI widgets (`docker_monitor/gui/widgets/`)**
	- `docker_terminal.py`: Sandboxed terminal enforcing `docker`-prefixed commands, background execution, history navigation, and tab completion.
	- `copy_tooltip.py`: Lightweight tooltip overlay used when copying IDs from the UI.
	- `ui_components.py`: Central factory for styled buttons, stat cards, and mouse-wheel bindings shared across managers.

- **Background workers & utilities (`docker_monitor/utils/`)**
	- `docker_utils.py`: Owns the global Docker SDK client, scaling logic, shared queues, and auto-scaling thresholds used by GUI managers.
	- `worker.py`: Thread-pool helper with bounded queues that funnels SDK calls off the Tk main loop while safely marshaling callbacks back to the UI.
	- `process_worker.py`: Process-pool helper for long-running or blocking CLI commands (e.g., image pulls) to avoid freezing threads.
	- `observer.py`: Observer/Subject implementation for emitting UI update events in a thread-safe manner.
	- `buffer_handler.py`: In-memory log buffer feeding the GUI log pane and exported diagnostics.

## Security notes

- Restricted command surface: The embedded terminal widget intentionally restricts input to commands that start with `docker` and the `clear` command. This reduces the risk that an attacker or a mistaken paste executes arbitrary shell commands from within the GUI. The terminal implementation validates and sanitizes inputs before invoking them through the Docker SDK or a subprocess.

- Privileged operations: Some helpers (notably `dmm-config`) run system-level package manager or policy commands that require `sudo`. Actions are emitted to the console before they execute so administrators know what will happen. Review the printed commands carefully when running on shared systems.

- Principle of least privilege: The app aims to use the Docker SDK where possible rather than invoking shell commands. When shell execution is necessary, arguments are validated and executed with minimal privileges. Users are encouraged to review and understand any prompts that request elevated permissions.

- Not a security boundary: While the embedded restrictions improve safety, the project is not designed to be a hardened security boundary against a determined attacker. For high-security environments, prefer audited orchestrators and restricted user policies.

## Troubleshooting (summary)

- Permission errors accessing Docker: If the GUI or CLI reports permission denied errors when talking to the Docker socket, first confirm the Docker daemon is running (`systemctl status docker` on systemd systems). If the daemon is running, add your user to the `docker` group to allow non-root access (`sudo usermod -aG docker $USER`) and re-login. `dmm-doctor` can detect and offer guidance for resolving common permission and configuration problems.

- AppArmor/SELinux interference: Security frameworks such as AppArmor (common on Ubuntu) or SELinux (common on Fedora/RHEL) can block container operations or filesystem access required by the app. Use `dmm-config` to inspect current profiles and, if necessary, switch AppArmor to complain mode for Docker (`aa-complain <profile>`) or follow distribution-specific guidance to adjust SELinux booleans. Make such changes only when you understand the security implications.

- Container lifecycle problems: If containers are not starting or clones misbehave, run `dmm-test` to create minimal test containers and validate monitoring and clone behavior. Inspect logs in the GUI's log panel and run `dmm-doctor` for additional diagnostics.

- Crashes and exceptions: Check the application's log view to capture stack traces. If a Python exception originates from the application code, run the quick import/compile checks (`python3 -m py_compile ...` and `python3 -c "import docker_monitor.main as m; print('OK')"`) to confirm your environment's Python packages are intact. When reporting issues, include the output from `dmm-doctor` and a copy of the recent application logs.

## Developer quick checks and tests

- Quick syntax test:
	- python3 -m py_compile docker_monitor/*.py

- Quick import test:
	- python3 -c "import docker_monitor.main as m; print('OK')"

- Build releases:
	- pip install build
	- python -m build

## Notes, assumptions and next steps

- Assumptions: This report is based primarily on `README.md` and the repository layout. Where runtime or packaging specifics are not available in code, this report follows the README instructions.
- Suggested next steps (optional): add a minimal CONTRIBUTING.md to document how to run tests and submit patches; add CI for linting and packaging to catch regressions early; add a short quickstart GIF/screenshots to `README.md` for visual onboarding.

---

