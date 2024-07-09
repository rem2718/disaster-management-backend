from tkinter import messagebox, ttk
import tkinter as tk
import requests
import getmac
import nmap

from config import config

token = dev_name = dev_password = broker_addr = broker_name = None
login_url = f"{config.get('FLASK_URL')}/api/users/login"
dev_reg_url = f"{config.get('FLASK_URL')}/api/devices/"
broker_url = f"{config.get('FLASK_URL')}/api/devices/broker_id"
update_broker_url = f"{config.get('FLASK_URL')}/api/devices/broker"
device_type_options = ["UGV", "UAV", "DOG", "CHARGING_STATION"]
subnet = config.get("SUBNET")
skipped = False


def get_mac(ip=None):
    mac_address = getmac.get_mac_address(ip=ip)
    return mac_address


def scan_for_mqtt_brokers():
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments="-p 1883 --open")
    brokers = []
    for host in nm.all_hosts():
        if nm[host]["tcp"][1883]["state"] == "open":
            brokers.append(host)
    return brokers[0] if brokers else ""


def get_broker_id(mac, token):
    params = {"mac": mac}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(broker_url, params=params, headers=headers)
    res = response.json()
    broker_id = res["broker_id"]
    broker_name = res["broker_name"]
    return broker_id, broker_name


def skip(login_window, options, broker, root):
    global skipped
    skipped = True
    options.destroy()
    broker.destroy()
    login_window.destroy()
    root.destroy()


def login(username, password, login_window, options):
    global token
    data = {"email_or_username": username, "password": password}
    try:
        response = requests.post(login_url, json=data)
        response.raise_for_status()
        token = response.json().get("token")
        if token:
            options.deiconify()
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid token received.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to login: {e}")


def submit(name, password, mac, type, result_label, broker_ip, root, broker):
    global dev_name, dev_password, broker_addr, broker_name
    dev_name, dev_password, broker_addr = name, password, broker_ip
    broker_mac = get_mac(broker_ip)
    broker_id, broker_name = get_broker_id(broker_mac, token)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": name,
        "password": password,
        "mac": mac,
        "type": type,
        "broker_id": broker_id,
    }
    try:
        response = requests.post(dev_reg_url, json=data, headers=headers)
        response.raise_for_status()

        if response.status_code == 201:
            result_label.config(text="Request sent successfully!", foreground="green")
            broker.destroy()
            root.destroy()
        else:
            res = response.json()
            result_label.config(
                text=f"Failed to send request: {res['message']}", foreground="red"
            )
    except requests.RequestException as e:
        result_label.config(text=f"Failed to send request: {e}", foreground="red")


def open_register(root, options):
    root.deiconify()
    options.destroy()


def open_broker(broker, options):
    broker.deiconify()
    options.destroy()


def config_submit(name, password, broker_ip, result_label, root):
    global dev_name, dev_password, broker_addr, broker_name
    dev_name, dev_password, broker_addr = name, password, broker_ip
    broker_mac = get_mac(broker_ip)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": name,
        "password": password,
        "broker_mac": broker_mac,
    }
    try:
        response = requests.put(update_broker_url, json=data, headers=headers)
        response.raise_for_status()
        res = response.json()
        if response.status_code == 200:
            result_label.config(text="Request sent successfully!", foreground="green")
            broker_name = res["broker_name"]
            root.destroy()
        else:
            result_label.config(
                text=f"Failed to send request: {res['message']}", foreground="red"
            )
    except requests.RequestException as e:
        result_label.config(text=f"Failed to send request: {e}", foreground="red")


def config_interface():
    print("configuring the robot...")
    broker_ip = scan_for_mqtt_brokers()
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
        login_window, text="If you already configure this robot before, click skip."
    )
    note_label.grid(row=3, columnspan=2, pady=10)

    login_button = tk.Button(
        login_window,
        text="Login",
        command=lambda: login(
            username_entry.get(), password_entry.get(), login_window, options
        ),
    )
    login_button.grid(row=4, column=0, padx=10, pady=10)

    skip_button = tk.Button(
        login_window,
        text="Skip",
        command=lambda: skip(login_window, options, broker, root),
    )
    skip_button.grid(row=4, column=1, padx=10, pady=10)

    options = tk.Tk()
    options.title("Configuration Options")
    options.withdraw()

    options_title = tk.Label(options, text="Choose what option you want:")
    options_title.grid(row=0, columnspan=2, pady=5)

    register_button = tk.Button(
        options,
        text="Register a new robot",
        command=lambda: open_register(root, options),
    )
    register_button.grid(row=1, column=0, pady=15)

    broker_button = tk.Button(
        options,
        text="Configure a new broker",
        command=lambda: open_broker(broker, options),
    )
    broker_button.grid(row=1, column=2, pady=15, padx=10)

    broker = tk.Tk()
    broker.title("Broker Configuration")
    broker.withdraw()
    broker_title = tk.Label(broker, text="fill the following information:")
    broker_title.grid(row=0, columnspan=2, pady=5)
    label_robot_name = tk.Label(broker, text="Device Name:")
    label_robot_name.grid(row=1, column=0, pady=5)
    entry_robot_name = tk.Label(broker, text=config.get("NAME"))
    entry_robot_name.grid(row=1, column=1, pady=5)

    label_broker_ip = tk.Label(broker, text="Broker IP address:")
    label_broker_ip.grid(row=2, column=0, pady=5)
    entry_broker_ip = tk.Entry(broker)
    entry_broker_ip.grid(row=2, column=1, pady=5, padx=10)
    entry_broker_ip.insert(0, broker_ip)

    config_button = tk.Button(
        broker,
        text="Submit",
        command=lambda: config_submit(
            config.get("NAME"),
            config.get("PASSWORD"),
            entry_broker_ip.get(),
            result_label_1,
            root,
        ),
    )
    config_button.grid(row=3, columnspan=2, pady=10)
    result_label_1 = tk.Label(broker, text="")
    result_label_1.grid(row=4, columnspan=2, pady=10)

    root = tk.Tk()
    root.title("Device Registration Form")
    root.withdraw()
    label_device_name = tk.Label(root, text="Device Name:")
    label_device_name.grid(row=0, column=0, pady=5)
    entry_device_name = tk.Entry(root)
    entry_device_name.grid(row=0, column=1, pady=5)

    label_device_password = tk.Label(root, text="Device Password:")
    label_device_password.grid(row=1, column=0, pady=5)
    entry_device_password = tk.Entry(root, show="*")
    entry_device_password.grid(row=1, column=1, pady=5)

    label_device_mac = tk.Label(root, text="Device MAC:")
    label_device_mac.grid(row=2, column=0, pady=5)
    entry_device_mac = tk.Entry(root)
    entry_device_mac.insert(0, get_mac())
    entry_device_mac.grid(row=2, column=1, pady=5)

    label_device_type = tk.Label(root, text="Device Type:")
    label_device_type.grid(row=3, column=0, pady=5)
    entry_device_type = ttk.Combobox(root, values=device_type_options)
    entry_device_type.grid(row=3, column=1, pady=5)
    entry_device_type.set("UGV")

    label_device_broker = tk.Label(root, text="Broker IP Address:")
    label_device_broker.grid(row=4, column=0, pady=5)
    entry_device_broker = tk.Entry(root)
    entry_device_broker.insert(0, broker_ip)
    entry_device_broker.grid(row=4, column=1, pady=5)

    note = "Note: The MAC address and broker IP Address are detected automatically.\nChange them if they are incorrect"

    note_label = tk.Label(root, text=note)
    note_label.grid(row=5, columnspan=2, pady=10)

    submit_button = tk.Button(
        root,
        text="Submit",
        command=lambda: submit(
            entry_device_name.get(),
            entry_device_password.get(),
            entry_device_mac.get(),
            (device_type_options.index(entry_device_type.get()) + 1),
            result_label,
            entry_device_broker.get(),
            root,
            broker
        ),
    )
    submit_button.grid(row=6, columnspan=2, pady=10)
    result_label = tk.Label(root, text="")
    result_label.grid(row=7, columnspan=2, pady=10)

    root.mainloop()

    if skipped:
        data = {"BROKER_ADDR": broker_ip}
    else:
        data = {
            "NAME": dev_name,
            "PASSWORD": dev_password,
            "BROKER_ADDR": broker_ip,
            "BROKER_NAME": broker_name,
        }
    return skipped, data

