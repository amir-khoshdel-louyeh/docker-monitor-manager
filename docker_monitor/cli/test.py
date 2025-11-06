#!/usr/bin/env python3
"""
dmm-test: Minimal test container creator for docker-monitor-manager

This script creates three simple test containers used by the project:
- dmm-test-nginx
- dmm-test-redis
- dmm-test-postgres
"""
from __future__ import annotations

import subprocess
import sys
import time
from typing import List


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def run_docker(args: List[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run a docker command"""
    cmd = ['docker'] + args
    try:
        if capture:
            return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        else:
            return subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"{Colors.RED}Error running docker command: {e}{Colors.ENDC}")
        return subprocess.CompletedProcess(cmd, returncode=1, stdout='', stderr=str(e))


def print_header(text: str):
    print(f"\n{text}\n{'-'*len(text)}")


def print_status(name: str, status: str, extra: str = ""):
    print(f"{name}: {status}")
    if extra:
        print(f"  -> {extra}")


def cleanup_existing_test_containers():
    """Remove existing test containers"""
    print_header("Cleaning up existing test containers")
    
    test_prefixes = ['dmm-test-', 'test-nginx']
    
    # Get all containers (including stopped)
    result = run_docker(['ps', '-a', '--format', '{{.Names}}'])
    if result.returncode != 0:
        print(f"{Colors.RED}Failed to list containers{Colors.ENDC}")
        return
    
    containers = [c for c in result.stdout.strip().split('\n') if c]
    
    # Filter and remove test containers using list comprehension
    test_containers = [c for c in containers if any(c.startswith(prefix) for prefix in test_prefixes)]
    
    # Remove containers (sequential to avoid race conditions)
    for container in test_containers:
        print(f"Removing: {container}")
        run_docker(['rm', '-f', container], capture=False)
    
    removed_count = len(test_containers)
    if removed_count > 0:
        print(f"\n{Colors.GREEN}✓ Removed {removed_count} test container(s){Colors.ENDC}")
    else:
        print(f"{Colors.CYAN}No test containers found{Colors.ENDC}")


def create_normal_containers():
    """Create normal working containers"""
    print_header("Creating normal containers")

    containers = [
        ('dmm-test-nginx', 'nginx:alpine', ['-p', '8080:80']),
        ('dmm-test-redis', 'redis:alpine', ['-p', '6379:6379']),
        ('dmm-test-postgres', 'postgres:alpine', ['-e', 'POSTGRES_PASSWORD=test123', '-p', '5432:5432']),
    ]

    for name, image, extra_args in containers:
        print(f"Pulling image: {image}")
        run_docker(['pull', image], capture=False)

        # Build the docker run command
        cmd_args = ['run', '-d', '--name', name] + extra_args + [image]
        result = run_docker(cmd_args)

        if result.returncode == 0:
            print_status(name, 'created')
        else:
            print_status(name, 'failed', result.stderr.strip())





def show_container_status():
    """Display status of all test containers"""
    print_header("Test containers status")

    result = run_docker(['ps', '-a', '--filter', 'name=dmm-test-', '--format', '{{.Names}}\t{{.Status}}\t{{.Image}}'])

    if result.returncode == 0:
        print(result.stdout)
    else:
        print('Failed to get container status')
def main(argv=None):
    """Main entry point"""
    if argv is None:
        argv = sys.argv[1:]

    command = None
    if argv:
        candidate = argv[0].lower()
        if candidate in ('-h', '--help'):
            print('Usage: dmm-test [cleanup|status]')
            return 0
        if candidate in ('cleanup', 'status'):
            command = candidate
        else:
            print(f"Unknown command: {argv[0]}")
            print('Usage: dmm-test [cleanup|status]')
            return 1
    
    # Check if Docker is available
    result = run_docker(['ps'])
    if result.returncode != 0:
        print(f"{Colors.RED}Error: Docker is not running or not accessible{Colors.ENDC}")
        print(f"\nPlease run: {Colors.CYAN}dmm-doctor{Colors.ENDC} to diagnose issues")
        return 1
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🧪 Docker Monitor Manager - Test Environment{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    if command == 'cleanup':
        cleanup_existing_test_containers()
        return 0
    
    if command == 'status':
        show_container_status()
        return 0
    
    # Cleanup before creating new containers
    cleanup_existing_test_containers()

    # Create normal containers
    create_normal_containers()
    
    # Show final status
    time.sleep(2)  # Wait a bit for containers to settle
    show_container_status()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}✓ Test environment ready!{Colors.ENDC}")
    print(f"\n{Colors.CYAN}You can now test docker-monitor-manager with:{Colors.ENDC}")
    print(f"  {Colors.BOLD}dmm{Colors.ENDC}\n")
    print(f"{Colors.CYAN}To cleanup test containers:{Colors.ENDC}")
    print(f"  {Colors.BOLD}dmm-test cleanup{Colors.ENDC}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
