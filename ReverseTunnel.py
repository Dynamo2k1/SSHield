#!/usr/bin/env python3
"""
Cool Reverse Tunnel
-------------------
This super cool script sets up a reverse port forwarding tunnel over SSH.
It connects to an SSH server and creates a tunnel that forwards a port
from the remote SSH server back to a destination reachable from the local machine.
It's like magic—but way cooler!
"""

import argparse
import getpass
import os
import socket
import select
import sys
import threading
import logging
import time
import paramiko

# ANSI color codes for cool colored output
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
RESET   = "\033[0m"

# Configure logging with colors
logging.basicConfig(
    level=logging.INFO,
    format=f"{CYAN}[%(asctime)s]{RESET} {YELLOW}%(levelname)s{RESET}: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

SSH_DEFAULT_PORT = 22
DEFAULT_REMOTE_PORT = 4000

def print_banner():
    banner = f"""
{MAGENTA}
  _________             .__.__          __  .__                 
 /   _____/__.__. _____ |__|  |   ____ |  | |__| ______ ____    
 \\_____  <   |  |/     \\|  |  | _/ __ \\|  | |  |/  ___// __ \\   
 /        \\___  |  Y Y  \\  |  |_\  ___/|  |_|  |\\___ \\  ___/   
/_______  / ____|__|_|  /__|____/\\___  >____/__|/____  >\\___  >
        \\/\\/          \\/          \\/              \\/     \\/

   {BLUE}Reverse Port Forwarding Tunnel - Super Cool Edition{RESET}
{RESET}
    """
    print(banner)

def handle_channel(chan, target_host, target_port):
    """Handle an incoming channel and tunnel data between the channel and the target."""
    try:
        sock = socket.socket()
        sock.connect((target_host, target_port))
    except Exception as e:
        logger.error(f"Failed to connect to {target_host}:{target_port}: {e}")
        chan.close()
        return

    logger.info(f"Tunnel OPEN: {chan.origin_addr} --> {chan.getpeername()} --> ({target_host}, {target_port})")
    while True:
        r, _, _ = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if not data:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if not data:
                break
            sock.send(data)
    chan.close()
    sock.close()
    logger.info(f"Tunnel CLOSED from {chan.origin_addr}")

def reverse_forward_tunnel(remote_port, target_host, target_port, transport):
    try:
        transport.request_port_forward("", remote_port)
        logger.info(f"Reverse forwarding established: remote port {remote_port} will forward to {target_host}:{target_port}")
    except Exception as e:
        logger.error(f"Failed to request port forward: {e}")
        sys.exit(1)

    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handle_channel, args=(chan, target_host, target_port))
        thr.setDaemon(True)
        thr.start()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Cool Reverse Tunnel - Set up a reverse forwarding tunnel over SSH.",
        epilog="Example: %(prog)s -r 127.0.0.1:80 mysshserver.com -p 9000"
    )
    parser.add_argument("ssh_server", help="SSH server address (hostname or IP)")
    parser.add_argument("-P", "--port", type=int, default=SSH_DEFAULT_PORT,
                        help=f"SSH server port (default: {SSH_DEFAULT_PORT})")
    parser.add_argument("-u", "--username", default=getpass.getuser(),
                        help="SSH username (default: current user)")
    parser.add_argument("-k", "--keyfile", help="Path to the private key file for SSH authentication")
    parser.add_argument("--no-key", dest="look_for_keys", action="store_false", default=True,
                        help="Do not look for keys when authenticating")
    parser.add_argument("-p", "--remote-port", type=int, default=DEFAULT_REMOTE_PORT,
                        help=f"Remote port on the SSH server to forward (default: {DEFAULT_REMOTE_PORT})")
    parser.add_argument("-r", "--remote", required=True,
                        help="Destination host and port to forward to (format: host:port)")
    parser.add_argument("--password", action="store_true", help="Prompt for SSH password")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    return parser.parse_args()

def main():
    print_banner()
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    # Parse the remote destination host and port
    try:
        target_host, target_port = args.remote.split(":", 1)
        target_port = int(target_port)
    except Exception as e:
        logger.error(f"Invalid remote specification '{args.remote}'. Use host:port format. {e}")
        sys.exit(1)

    # Prompt for password if requested
    password = None
    if args.password:
        password = getpass.getpass("Enter SSH password: ")

    logger.info(f"Connecting to SSH server {args.ssh_server}:{args.port} as {args.username}")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    try:
        client.connect(
            args.ssh_server,
            args.port,
            username=args.username,
            key_filename=args.keyfile,
            look_for_keys=args.look_for_keys,
            password=password
        )
    except Exception as e:
        logger.error(f"Connection to {args.ssh_server}:{args.port} failed: {e}")
        sys.exit(1)

    logger.info(f"{GREEN}SSH connection established!{RESET}")
    transport = client.get_transport()
    reverse_forward_tunnel(args.remote_port, target_host, target_port, transport)

if __name__ == "__main__":
    main()
