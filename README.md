# Collection of Code Files for Different Components of the Disaster Management System

in linux always use python3
## HiveMQ Broker


## Mosquitto Broker
- The Mosquitto broker should be hosted on a device that is on the same LAN as the other robots.
- First, you should install Mosquitto, and then copy and paste the configuration file **mosquitto.conf** into your Mosquitto directory.
- place **acl_file.conf** inside your Mosquitto directory.
- You need to create two admin users, **admin-ugv**, **admin-broker**.
- The password for **admin-ugv** should be shared with other devices in order to register users. However, always ensure to save it in the .env file.
- **admin-broker** is the user that is used in **mqtt_bridge**.
- Don't forget to save the usernames and passwords in the .env file as the default values might not represent yours.
- A **.env** file will be provided to you; you have to adjust the values to suit your case.
- Finally, you need to run **mqtt_bridge.py** to bridge all the cloud packets to the HiveMQ broker.


## RTMP Server
- The RTMP Server should be hosted on the cloud using Nginx, along with the web server. Please refer to this [link](https://github.com/rem2718/disaster-management) for the web server.

- Ensure that you have Nginx installed first, and then copy and paste the configuration file **nginx.conf** into your Nginx configuration directory.

- ffmpeg


## UGV Codes

