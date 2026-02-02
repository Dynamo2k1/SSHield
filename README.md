# 🛡️ SSHield

<div align="center">

**The Ultimate SSH Reverse Tunneling & Remote Administration Suite**

</div>

---

## 📖 Overview

**SSHield** is a powerful, lightweight Python-based toolkit designed for secure network tunneling and remote system administration. Built on top of the robust `paramiko` library, it provides two core functionalities:

1. **Reverse Port Forwarding (`ReverseTunnel.py`)**: Expose local services to the internet securely behind NATs and firewalls by tunneling them through a remote SSH server.
2. **Encrypted Remote Shell (`server.py` & `client.py`)**: A custom SSH server and client pair that facilitates secure, interactive command execution and file management.

Whether you are a system administrator needing to bypass a strict firewall or a cybersecurity student studying traffic encapsulation, SSHield is your go-to tool.

---

## ✨ Features

### 🚀 Reverse Tunneling

* **Bypass Firewalls**: Access internal services (like a local web server) from the outside world.
* **Secure Transport**: All traffic is encrypted via standard SSH protocols.
* **Multi-Client Support**: Handles multiple connections efficiently.
* **Verbose Logging**: detailed, color-coded logs for debugging and monitoring traffic flow.

### 💻 Remote Shell (C2)

* **Interactive Shell**: Execute system commands on the client machine in real-time.
* **Built-in File Transfer**: Includes a `download` command to retrieve files from the client.
* **Directory Navigation**: Native support for `cd` to navigate the remote file system.
* **Custom SSH Server**: A standalone Python SSH server implementation.

---

## ⚙️ Installation

### Prerequisites

* Python 3.x
* `paramiko` library

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Dynamo2k1/SSHield.git
cd SSHield

```


2. **Install dependencies:**
```bash
pip install paramiko

```



---

## 🛠️ Usage Guide

### Module 1: Reverse Tunnel (`ReverseTunnel.py`)

This script connects to a standard SSH server and opens a port on *that* server which forwards traffic back to a target on your local network.

**Syntax:**

```bash
python3 ReverseTunnel.py [options] -r <dest_host>:<dest_port> <ssh_server>

```

**Common Options:**

* `-r, --remote`: The local destination to forward to (e.g., `127.0.0.1:80`).
* `-p, --remote-port`: The port to open on the SSH server (default: `4000`).
* `-u, --username`: SSH username.
* `-k, --keyfile`: SSH Private key (optional).
* `--password`: Prompt for a password.

**Example:**
Forward port `80` (Local Web Server) to port `9000` on your remote VPS (`myserver.com`):

```bash
python3 ReverseTunnel.py -r 127.0.0.1:80 myserver.com -p 9000 --username root --password

```

*Now, accessing `myserver.com:9000` will show the content of your local `127.0.0.1:80`.*

---

### Module 2: Remote Administration (`server.py` & `client.py`)

This module creates a custom SSH communication channel.

#### 1. Configure the Server

Before running `server.py`, you must ensure you have an RSA host key generated.

```bash
# Generate a key (if you don't have one)
ssh-keygen -t rsa -f test_rsa.key

```

*Note: Update the `host_key` path in `server.py` (line 47) to point to your generated key location.*

**Start the Server:**

```bash
python3 server.py <bind_ip> <port>
# Example:
python3 server.py 0.0.0.0 2222

```

#### 2. Start the Client

The client connects to your custom server.

```bash
python3 client.py <server_ip> <server_port> <username> <password>

```

* **Default Credentials** (Hardcoded in `server.py`):
* **User**: `dynamo`
* **Pass**: `1590`



**Example:**

```bash
python3 client.py 192.168.1.5 2222 dynamo 1590

```

#### 3. Interactive Commands

Once connected, the server terminal becomes a shell for the client machine.

* **Execute Commands**: Type any shell command (`ls`, `whoami`, `ipconfig`).
* **Change Directory**: `cd <path>`
* **Download Files**: `download <filename>`
* **Exit**: `exit`

---

## ⚠️ Disclaimer

**SSHield is for Educational and Authorized Use Only.**

This software is developed for network administration and cybersecurity research. The author (Rana Uzair Ahmad) is not responsible for any misuse of this tool. Always obtain proper authorization before setting up tunnels or remote connections on networks you do not own.

---

## 📜 License

This project is licensed under the **MIT License**.

**Copyright (c) 2025 Rana Uzair Ahmad**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction... (see `LICENSE` file for full text).

---

<div align="center">
<b>Developed with ❤️ by Rana Uzair Ahmad</b>
</div>

```

