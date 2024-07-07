# All my Work for Different Components of the Disaster Management System

## BACKEND

check the [documentation](https://docs.google.com/document/d/1gS4TmuDZGWw6IP3S2O6vt80A9_Mr-PaPovwCOnXrAaM) for more info

to run the backend:

- first clone this repo
- install docker if you dont have it already
- then create _.env_ file inside _flask/app_ directory
- fill _.env_ with the content of this [file](https://drive.google.com/file/d/1C97KQtfIIS75cXcdN4TfpVWwiihHWhpn/view?usp=sharing)
- open terminal inside this directory
- run this command

```
    docker-compose -p disaster-management up --build
```

- Note: if you found _Error: Connection refused_ in _mosquitto_server_ logs please do the following:

```
    docker exec -it mosquitto_server /bin/sh
    nohup /usr/local/bin/mosquitto_admin.sh /proc/1/fd/1 2>/proc/1/fd/2
    # then close the terminal
```

and voila! You have the whole backend running: a web server (Flask), an MQTT server (Mosquitto), an RTMP server, and Nginx

## BROKER PROGRAM

- the Mosquitto broker should be hosted on a device that is on the same LAN as the other robots
  -download _broker_program_ on your device
- install Mosquitto

```
sudo apt-get install -y mosquitto mosquitto-clients
```

- copy and paste the configuration file **mosquitto.conf** into your Mosquitto directory
- place **acl_file.conf** inside your Mosquitto directory
- create an empty file called _passwd_ with no extention and place it inside mosquitto directory
- you need to create two admin users, **admin-ugv**, **admin-broker**
- the password for **admin-ugv** should be shared with other devices in order to register users. However, always ensure to save it in the .env file.
- **admin-broker** is the user that is used in **mqtt_bridge**.
- Don't forget to save the usernames and passwords in the .env file as the default values might not represent yours.
- A **.env** file will be provided to you; you have to adjust the values to suit your case.
- create venv, activate it and install all reqs

```
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
```

- Finally, you need to run **mqtt_bridge.py**

```
    python3 mqtt_bridge.py
```

## UGV PROGRAM

- download _ugv_program_ on the robot
- install ffmpeg and nmap

```
    sudo apt-get install -y ffmpeg
    sudo apt-get install -y nmap
```

- _.env_ file will be given to you
- open the terminal on the same directory
- create venv, activate it and install all reqs

```
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
```

- run _main.py_

```
    python3 main.py
```

## AI

The UGV program already includes a Face recognition module. Before running it, you must train the model on team members' faces following these steps:

- create a _.env_ file and fill it with your information (Admin name and password, Flask server URL):

```
    USERNAME=
    PASSWORD=
    FLASK_URL=
```

- cd to the AI directory.

- create a virtual environment and activate it:

```
    #for windows:
    python -m venv .venv
    .venv/Scripts/Activate
    #for linux:
    python3 -m venv .venv
    source .venv/bin/activate
```

- install requirements:

```
    #for windows:
    pip install -r requirements.txt
    #for linux:
    pip3 instll -r requirements.txt
```
- run _face\_taker.py_. It will prompt you to enter your name and take at least 5 images of yourself. Try looking in different directions, making different facial gestures, and under varying lighting conditions to enhance the model's robustness.
- repeat the same process for all the team members.
- check the _images_ folder to ensure it contains a folder for each member.
- after preparing the images, edit the _init\_image_ variable in _face\_encoder.py_ to replace my name with yours.
- finally, execute _face\_encoder.py_ to train the model and send it to the Flask server. Once completed, you're done!