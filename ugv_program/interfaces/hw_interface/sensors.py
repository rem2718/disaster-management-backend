import random

def read_sensor_data():
    # TO-DO: read sensor data here
    temp = random.uniform(-20, 50)
    humidity = random.uniform(0, 100)
    gas = random.uniform(100, 1000)
    co2 = random.uniform(10, 200)
    tvoc = random.uniform(10, 200)
    gyroscope1 = random.uniform(0, 360)
    gyroscope2 = random.uniform(0, 360)
    gyroscope3 = random.uniform(0, 360)
    accelerometer1 = random.uniform(0, 360)
    accelerometer2 = random.uniform(0, 360)
    accelerometer3 = random.uniform(0, 360)
    ir = random.uniform(1,10)
    ultrasonic = random.uniform(0, 100)
    sound = random.uniform(0, 1000)
    battery = random.uniform(0, 100)
    
    data = [
        {
            "sensor": "temperature",
            "value": temp,
            "unit": "°C"
        },
        {
            "sensor": "humidity",
            "value": humidity,
            "unit": "%"
        },
        {
            "sensor": "gas",
            "value": gas,
            "unit": "ppm"
        },
        {
            "sensor": "co2",
            "value": co2,
            "unit": "ppm"
        },
        {
            "sensor": "tvoc",
            "value": tvoc,
            "unit": "ppb"
        },
        {
            "sensor": "accelerometer",
            "value": [
                accelerometer1,
                accelerometer2,
                accelerometer3
            ],
            "unit": "m/s^2"
        },
        {
            "sensor": "gyroscope",
            "value": [
                gyroscope1,
                gyroscope2,
                gyroscope3
            ],
            "unit": "°/s"
        },
        {
            "sensor": "ir",
            "value": ir,
            "unit": ""
        },
        {
            "sensor": "ultrasonic",
            "value": ultrasonic,
            "unit": "cm"
        },
        {
            "sensor": "sound",
            "value": sound,
            "unit": ""
        },
        {
            "sensor": "battery",
            "value": battery,
            "unit": "%"
        }
    ]
    return data


def get_gps():
    # TO-DO: read gps data here
    lat = random.uniform(-90, 90)
    long = random.uniform(-180, 180)
    gps = {"lat": lat, "long": long}
    return gps
