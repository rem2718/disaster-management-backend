import subprocess

from config import env_get


def create_mosquitto_user(username, password):
    try:
        sys_pass = env_get("SYS_PASS")

        add_user_command = [
            "sudo",
            "-S",
            "mosquitto_passwd",
            "-b",
            "/etc/mosquitto/passwd",
            username,
            password,
        ]

        result = subprocess.run(add_user_command, input=sys_pass.encode(), check=True)

        if result.returncode == 0:
            reload_command = [
                "sudo",
                "kill",
                "-HUP",
                str(subprocess.check_output(["pidof", "mosquitto"]).decode().strip()),
            ]
            subprocess.run(reload_command, check=True)

        print(f"User '{username}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create user '{username}': {e}")


def delete_mosquitto_user(username):
    try:
        sys_pass = env_get("SYS_PASS")

        add_user_command = [
            "sudo",
            "-S",
            "mosquitto_passwd",
            "-D",
            "/etc/mosquitto/passwd",
            username,
        ]

        result = subprocess.run(add_user_command, input=sys_pass.encode(), check=True)

        if result.returncode == 0:
            reload_command = [
                "sudo",
                "kill",
                "-HUP",
                str(subprocess.check_output(["pidof", "mosquitto"]).decode().strip()),
            ]
            subprocess.run(reload_command, check=True)

        print(f"User '{username}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create user '{username}': {e}")
