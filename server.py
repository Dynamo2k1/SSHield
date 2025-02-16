#!/usr/bin/env python3
import sys
import socket
import threading
import paramiko
from paramiko import RSAKey, SSHException
import traceback

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == "dynamo" and password == "1590":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def interactive_shell(chan):
    try:
        # Optionally, if the client sends an initial message, read it:
        if chan.recv_ready():
            initial_msg = chan.recv(8192).decode()
            print(initial_msg)

        while True:
            command = input("Enter command (or 'exit' to quit): ").strip()
            if not command:
                continue
            chan.send(command)
            if command.lower() == "exit":
                print("[-] Exiting!")
                break
            output = chan.recv(8192).decode()
            print(output)
    except KeyboardInterrupt:
        print("[-] Keyboard interrupt. Exiting.")
    except Exception as e:
        print("[-] Error: " + str(e))
    finally:
        chan.close()

def start_server(server_ip, server_port):
    host_key = RSAKey(filename="/home/dynamo/.ssh/test_rsa.key")  # Make sure you have this key.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_ip, server_port))
        sock.listen(100)
        print(f"[+] Listening for connection on {server_ip}:{server_port} ...")
    except Exception as e:
        print("[-] Socket setup failed:", e)
        sys.exit(1)

    try:
        client, addr = sock.accept()
        print(f"[+] Got a connection from {addr[0]}:{addr[1]}")
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)

        server = SSHServer()
        transport.start_server(server=server)

        chan = transport.accept(20)
        if chan is None:
            print("[-] No channel was opened.")
            return

        print("[+] Client authenticated!")
        interactive_shell(chan)
    except Exception as e:
        print("[-] Exception:", e)
        traceback.print_exc()
    finally:
        transport.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <server_ip> <port>")
        sys.exit(1)
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    start_server(server_ip, server_port)
