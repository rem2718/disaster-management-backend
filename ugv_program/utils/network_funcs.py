import requests
import getmac
import nmap

from config import Config

broker_url = f"{Config.FLASK_URL}/api/devices/broker_id"
subnet = Config.SUBNET


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

    if brokers:
        ip = brokers[0]
        mac = get_mac(ip=ip)
    else:
        ip, mac = "", ""
    return ip, mac


def broker_id(mac, token):
    params = {"mac": mac}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(broker_url, params=params, headers=headers)
    broker_id = response.json()["broker_id"]
    return broker_id
