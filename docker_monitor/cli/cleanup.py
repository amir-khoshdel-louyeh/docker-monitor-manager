#!/usr/bin/env python3
"""
dmm-cleanup: Docker Monitor Manager resource cleanup helper

This tool reclaims disk and memory by pruning unused Docker artifacts and
terminating lingering container shim processes.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from typing import List, Sequence, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def run_command(cmd: Sequence[str]) -> subprocess.CompletedProcess:
    """Run a command and return the completed process"""
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def format_bytes(size: int) -> str:
    """Return human-readable byte count"""
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == 'B':
                return f"{int(value)}{unit}"
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}PB"


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")


def print_step(title: str):
    print(f"{Colors.BOLD}{Colors.YELLOW}→ {title}{Colors.ENDC}")


def check_docker_available() -> bool:
    if shutil.which('docker') is None:
        print(f"{Colors.RED}✗ Docker CLI not found on PATH. Install Docker before running dmm-cleanup.{Colors.ENDC}")
        return False
    result = run_command(['docker', 'info'])
    if result.returncode != 0:
        print(f"{Colors.RED}✗ Unable to talk to Docker daemon: {result.stderr.strip()}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Tip:{Colors.ENDC} Ensure the Docker daemon is running and you have sufficient permissions.")
        return False
    return True


def prune(title: str, cmd: Sequence[str]) -> Tuple[bool, str]:
    """Run a docker prune command and return success + message."""
    result = run_command(cmd)
    if result.returncode == 0:
        output = result.stdout.strip() or 'Nothing to prune.'
        return True, output
    return False, result.stderr.strip() or 'Unknown error'


def cleanup_orphaned_container_memory() -> Tuple[bool, str]:
    """Detect and reclaim memory from orphaned container shim processes"""
    try:
        import psutil  # type: ignore
    except ImportError:
        return False, "psutil is not installed. Install it with 'pip install psutil'."

    all_containers = run_command(['docker', 'ps', '-a', '--no-trunc', '-q'])
    if all_containers.returncode != 0:
        return False, "Unable to list containers to verify memory cleanup"

    known_ids = {line.strip() for line in all_containers.stdout.splitlines() if line.strip()}

    orphaned: List[Tuple['psutil.Process', str, int]] = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            name = (proc.info.get('name') or '').lower()
        except psutil.Error:
            continue

        if 'containerd-shim' not in name:
            continue

        cmdline = proc.info.get('cmdline') or []
        container_id = None

        for idx, arg in enumerate(cmdline):
            if arg in ('-id', '--id') and idx + 1 < len(cmdline):
                container_id = cmdline[idx + 1]
                break

        if not container_id and cmdline:
            candidate = cmdline[-1]
            if len(candidate) >= 12 and all(ch in '0123456789abcdef' for ch in candidate.lower()[:12]):
                container_id = candidate

        if not container_id:
            continue

        if any(container_id.startswith(known) or known.startswith(container_id) for known in known_ids):
            continue

        inspect = run_command(['docker', 'inspect', container_id])
        if inspect.returncode == 0:
            # Container still exists; skip termination
            continue

        try:
            mem_info = proc.info.get('memory_info') or proc.memory_info()
            rss = int(getattr(mem_info, 'rss', 0))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        orphaned.append((proc, container_id, rss))

    if not orphaned:
        return True, "No orphaned container shims detected"

    total_reclaimed = 0
    failures: List[str] = []

    for proc, cid, rss in orphaned:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
            total_reclaimed += rss
        except (psutil.AccessDenied, psutil.NoSuchProcess) as exc:
            failures.append(f"{cid[:12]} ({exc})")

    if failures:
        details = ', '.join(failures)
        return False, f"Failed to clean some shims ({details}). Try rerunning with sudo."

    reclaimed_text = format_bytes(total_reclaimed)
    count = len(orphaned)
    plural = 's' if count != 1 else ''
    return True, f"Freed {reclaimed_text} from {count} orphaned container shim{plural}"


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if argv:
        if argv[0] in ('-h', '--help'):
            print("Usage: dmm-cleanup")
            print("Prunes unused Docker resources and frees memory from orphaned container shims.")
            return 0
        print('Unexpected argument(s):', ' '.join(argv))
        return 1

    if not check_docker_available():
        return 1

    print_header("Docker Monitor Manager - Cleanup Tool")
    print(f"{Colors.CYAN}This will prune unused Docker resources and try to reclaim memory from lingering shims.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Tip:{Colors.ENDC} Run with sudo if you see permission errors.\n")

    tasks = [
        ("Removing stopped containers", ['docker', 'container', 'prune', '--force']),
        ("Removing dangling images", ['docker', 'image', 'prune', '--force']),
        ("Removing unused networks", ['docker', 'network', 'prune', '--force']),
        ("Removing unused volumes", ['docker', 'volume', 'prune', '--force']),
    ]

    success = True

    for title, cmd in tasks:
        print_step(title)
        ok, message = prune(title, cmd)
        if ok:
            print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}\n")
        else:
            success = False
            print(f"{Colors.RED}✗ {message}{Colors.ENDC}\n")

    print_step("Releasing orphaned container memory")
    mem_ok, mem_message = cleanup_orphaned_container_memory()
    if mem_ok:
        print(f"{Colors.GREEN}✓ {mem_message}{Colors.ENDC}\n")
    else:
        success = False
        print(f"{Colors.RED}✗ {mem_message}{Colors.ENDC}\n")

    print_header("Cleanup Summary")
    if success:
        print(f"{Colors.GREEN}✓ Cleanup completed successfully.{Colors.ENDC}")
        return 0

    print(f"{Colors.YELLOW}⚠ Cleanup finished with some issues. Review messages above for details.{Colors.ENDC}")
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
