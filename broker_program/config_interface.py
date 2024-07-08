from tkinter import messagebox
import tkinter as tk
import requests
import getmac

from config import config

token = dev_name = dev_password = None
login_url = f"{config.get('FLASK_URL')}/api/users/login"
dev_reg_url = f"{config.get('FLASK_URL')}/api/devices/"
subnet = config.get("SUBNET")
skipped = False
broker_type = 5


def get_mac(ip=None):
    mac_address = getmac.get_mac_address(ip=ip)
    return mac_address


def skip(login_window, root):
    global skipped
    skipped = True
    login_window.destroy()
    root.destroy()


def login(username, password, login_window, root):
    global token
    data = {"email_or_username": username, "password": password}
    try:
        response = requests.post(login_url, json=data)
        response.raise_for_status()
        token = response.json().get("token")
        if token:
            root.deiconify()
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid token received.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to login: {e}")


def submit(name, password, mac, result_label):
    global dev_name, dev_password
    dev_name, dev_password = name, password
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": name,
        "password": password,
        "mac": mac,
        "type": broker_type,
    }
    try:
        response = requests.post(dev_reg_url, json=data, headers=headers)
        response.raise_for_status()

        if response.status_code == 201:
            result_label.config(text="Request sent successfully!", foreground="green")
        else:
            res = response.json()
            result_label.config(
                text=f"Failed to send request: {res['message']}", foreground="red"
            )
    except requests.RequestException as e:
        result_label.config(text=f"Failed to send request: {e}", foreground="red")


def config_interface():
    print("configuring the broker...")
    login_window = tk.Tk()
    login_window.title("Login")

    note_label = tk.Label(login_window, text="Enter your Admin creds:")
    note_label.grid(row=0, columnspan=2, pady=10)

    tk.Label(login_window, text="Username:").grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Password:").grid(row=2, column=0, padx=10, pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=5)

    note_label = tk.Label(
        login_window, text="If you already configure this broker before, click skip."
    )
    note_label.grid(row=3, columnspan=2, pady=10)

    login_button = tk.Button(
        login_window,
        text="Login",
        command=lambda: login(
            username_entry.get(), password_entry.get(), login_window, root
        ),
    )
    login_button.grid(row=4, column=0, padx=10, pady=10)

    skip_button = tk.Button(
        login_window,
        text="Skip",
        command=lambda: skip(login_window, root),
    )
    skip_button.grid(row=4, column=1, padx=10, pady=10)

    root = tk.Tk()
    root.title(f"Broker Registration Form")
    root.withdraw()

    label_device_name = tk.Label(root, text="Broker Name:")
    label_device_name.grid(row=0, column=0, pady=5)
    entry_device_name = tk.Entry(root)
    entry_device_name.grid(row=0, column=1, pady=5)

    label_device_password = tk.Label(root, text="Broker Password:")
    label_device_password.grid(row=1, column=0, pady=5)
    entry_device_password = tk.Entry(root, show="*")
    entry_device_password.grid(row=1, column=1, pady=5)

    label_device_mac = tk.Label(root, text="Broker MAC:")
    label_device_mac.grid(row=2, column=0, pady=5)
    entry_device_mac = tk.Entry(root)
    entry_device_mac.insert(0, get_mac())
    entry_device_mac.grid(row=2, column=1, pady=5)

    note = "Note: The MAC address is detected automatically.\nYou can change them if they are incorrect"

    note_label = tk.Label(root, text=note)
    note_label.grid(row=3, columnspan=2, pady=10)

    submit_button = tk.Button(
        root,
        text="Submit",
        command=lambda: submit(
            entry_device_name.get(),
            entry_device_password.get(),
            entry_device_mac.get(),
            result_label,
        ),
    )
    submit_button.grid(row=4, columnspan=2, pady=10)

    result_label = tk.Label(root, text="")
    result_label.grid(row=5, columnspan=2, pady=10)

    root.mainloop()
    data = {}
    if not skipped:
        data = {"name": dev_name, "password": dev_password}
    return skipped, data
