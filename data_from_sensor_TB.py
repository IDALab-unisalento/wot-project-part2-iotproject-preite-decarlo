import os
import time
import sys
import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json
from random import randint

THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = '0iHKnpBpX6DoTd7Zrx6N'

# Data capture and upload interval in seconds. Less interval will eventually ha$
INTERVAL=2

sensor_data = {'temperature': 0, 'humidity': 0, 'latitude': 0, 'longitude':0}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive inter$
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()

try:
    while True:
    
        humidity,temperature = dht.read_retry(dht.DHT11, 4)
        
        product_id = randint(1,10)
        
        humidity = round(humidity, 2)
        temperature = round(temperature, 2)

        latitude = 40.3349463
		longitude = 18.1189842

        if product_id == 1:
            latitude = 40.3349463
            longitude = 18.1189842

        if product_id == 2:
            latitude = 40.3451522 
            longitude = 18.1458633
            
        if product_id == 3:
            latitude = 40.3499907
            longitude = 18.1728663

        if product_id == 4:
            latitude = 40.353022
            longitude = 18.1744746

        if product_id == 5:
            latitude = 40.3534742
                        longitude = 18.1726547

        if product_id == 6:
            latitude = 40.3570543
            longitude = 18.1684222
                
        print(u"Temperature: {0:0.1f}*C, Humidity: {1:0.1f}%".format(temperatur$
        print("Latitude: " + str(latitude) + "*," + " Longitude: " + str(longit$
        sensor_data['temperature'] = temperature
        sensor_data['humidity'] = humidity
                sensor_data['latitude'] = latitude
        sensor_data['longitude'] = longitude

        print(sensor_data)

        # Sending humidity and temperature data to ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
		        if sleep_time > 0:
            time.sleep(sleep_time)
            
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()