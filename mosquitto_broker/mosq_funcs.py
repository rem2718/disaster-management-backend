import subprocess

from config import env_get


def create_mosquitto_user(username, password):
    try:
        command = f"echo '{env_get("SYS_PASS")}' | sudo -S mosquitto_passwd -b /etc/mosquitto/passwd {username} {password}"
        subprocess.run(command, shell=True, check=True)
        print(f"User '{username}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create user '{username}': {e}")


def delete_mosquitto_user(username):
    try:
        command = f"echo '{env_get("SYS_PASS")}' | sudo -S mosquitto_passwd -D /etc/mosquitto/passwd {username}"
        subprocess.run(command, shell=True, check=True)
        print(f"User '{username}' deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to delete user '{username}': {e}")