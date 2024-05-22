# All my Work for Different Components of the Disaster Management System

## BACKEND
check the [documentation](https://docs.google.com/document/d/1gS4TmuDZGWw6IP3S2O6vt80A9_Mr-PaPovwCOnXrAaM) for more info

to run the backend:
- first clone this repo 
- install docker if you dont have it already.
- then create _.env_ file inside _flask/app_ directory
- fill _.env_ with the content of this [file](https://drive.google.com/file/d/1C97KQtfIIS75cXcdN4TfpVWwiihHWhpn/view?usp=sharing)
- open terminal inside this directory
- run this command
```
    docker-compose -p disaster-management up --build
```

and voila! You have the whole backend running: a web server (Flask), an MQTT server (Mosquitto), an RTMP server, and Nginx.


## BROKER PROGRAM
- The Mosquitto broker should be hosted on a device that is on the same LAN as the other robots.
- First, you should install Mosquitto, and then copy and paste the configuration file **mosquitto.conf** into your Mosquitto directory.
- place **acl_file.conf** inside your Mosquitto directory.
- You need to create two admin users, **admin-ugv**, **admin-broker**.
- The password for **admin-ugv** should be shared with other devices in order to register users. However, always ensure to save it in the .env file.
- **admin-broker** is the user that is used in **mqtt_bridge**.
- Don't forget to save the usernames and passwords in the .env file as the default values might not represent yours.
- A **.env** file will be provided to you; you have to adjust the values to suit your case.
- Finally, you need to run **mqtt_bridge.py** to bridge all the cloud packets to the HiveMQ broker.


## UGV PROGRAM


## NOTES
- in linux always use python3, pip3