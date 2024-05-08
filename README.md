# Collection of Code Files for Different Components of the Disaster Management System

## HiveMQ Broker


## Mosquitto Broker
- The Mosquitto broker should be hosted on a device that is on the same LAN as the other robots.
- First, you should install Mosquitto, and then copy and paste the configuration file _mosquitto.conf_ into your Mosquitto configuration directory.
- A _.env_ file will be provided to you; you have to adjust the values to suit your case.
- Finally, you need to run _mqtt\_bridge.py_ to bridge all the cloud packets to the HiveMQ broker.


## RTMP Server
- The RTMP Server should be hosted on the cloud using Nginx, along with the web server. Please refer to this [link](https://github.com/rem2718/disaster-management) for the web server.

- Ensure that you have Nginx installed first, and then copy and paste the configuration file _nginx.conf_ into your Nginx configuration directory.


## UGV Codes

