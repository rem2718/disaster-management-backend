from tkinter import messagebox, ttk
import tkinter as tk
import requests
import getmac
import nmap

from config import Config

token, dev_name, dev_password = None, None, None
login_url = f"{Config.FLASK_URL}/api/users/login"
dev_reg_url = f"{Config.FLASK_URL}/api/devices"
subnet = Config.SUBNET
default_type = Config.DEFAULT_TYPE
device_type_options = ["UGV", "UAV", "DOG", "CHARGING_STATION", "BROKER"]

print(default_type)


def get_mac():
    mac_address = getmac.get_mac_address()
    return mac_address


def scan_for_mqtt_brokers():
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments="-p 1883 --open")
    brokers = []
    for host in nm.all_hosts():
        if nm[host]["tcp"][1883]["state"] == "open":
            brokers.append(host)
    ip = brokers[0] if brokers else ""
    return ip


def login(username, password, root, login_window):
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


def submit(name, password, mac, type, result_label):
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
        "type": type,
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


def conf_interface():
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

    login_button = tk.Button(
        login_window,
        text="Login",
        command=lambda: login(
            username_entry.get(), password_entry.get(), root, login_window
        ),
    )
    login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    root = tk.Tk()
    dev = "Broker" if default_type == "BROKER" else "Device"
    root.title(f"{dev} Registration Form")
    root.withdraw()

    label_device_name = tk.Label(root, text=f"{dev} Name:")
    label_device_name.grid(row=0, column=0, pady=5)
    entry_device_name = tk.Entry(root)
    entry_device_name.grid(row=0, column=1, pady=5)

    label_device_password = tk.Label(root, text=f"{dev} Password:")
    label_device_password.grid(row=1, column=0, pady=5)
    entry_device_password = tk.Entry(root, show="*")
    entry_device_password.grid(row=1, column=1, pady=5)

    label_device_mac = tk.Label(root, text=f"{dev} MAC:")
    label_device_mac.grid(row=2, column=0, pady=5)
    entry_device_mac = tk.Entry(root)
    entry_device_mac.insert(0, get_mac())
    entry_device_mac.grid(row=2, column=1, pady=5)

    label_device_type = tk.Label(root, text=f"{dev} Type:")
    label_device_type.grid(row=3, column=0, pady=5)
    entry_device_type = ttk.Combobox(root, values=device_type_options)
    entry_device_type.grid(row=3, column=1, pady=5)
    entry_device_type.set(default_type)

    if default_type != "BROKER":
        label_device_broker = tk.Label(root, text="Broker ID:")
        label_device_broker.grid(row=4, column=0, pady=5)
        entry_device_broker = tk.Entry(root)
        entry_device_broker.insert(0, scan_for_mqtt_brokers())
        entry_device_broker.grid(row=4, column=1, pady=5)

    rw = 4 if default_type == "BROKER" else 5

    if default_type != "BROKER":
        note = "Note: The MAC address and broker ID are detected automatically.\nYou can change them if they are incorrect"
    else:
        note = "Note: The MAC address is detected automatically.\nYou can change them if they are incorrect"

    note_label = tk.Label(root, text=note)
    note_label.grid(row=rw, columnspan=2, pady=10)

    submit_button = tk.Button(
        root,
        text="Submit",
        command=lambda: submit(
            entry_device_name.get(),
            entry_device_password.get(),
            entry_device_mac.get(),
            (device_type_options.index(entry_device_type.get()) + 1),
            result_label,
        ),
    )
    submit_button.grid(row=rw + 1, columnspan=2, pady=10)

    result_label = tk.Label(root, text="")
    result_label.grid(row=rw + 2, columnspan=2, pady=10)

    root.mainloop()
    return dev_name, dev_password
