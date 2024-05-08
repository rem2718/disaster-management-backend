import subprocess


def create_mosquitto_user(username, password):
    try:
        subprocess.run(
            ["mosquitto_passwd", "-b", "/etc/mosquitto/passwd", username, password],
            check=True,
        )
        print(f"User '{username}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create user '{username}': {e}")


def delete_mosquitto_user(username):
    try:
        subprocess.run(
            ["mosquitto_passwd", "-D", "/etc/mosquitto/passwd", username], check=True
        )
        print(f"User '{username}' deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to delete user '{username}': {e}")


username = "alice"
password = "1234qwe"
create_mosquitto_user(username, password)

delete_mosquitto_user(username)
