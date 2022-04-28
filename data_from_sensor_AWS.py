from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time
import json
import datetime
from random import randint

global control
control = "on"

# Custom MQTT message callback
# This function is invoked when a message is posted on device shadow topic.
# This is how we will control the device from Lambda function running in AWS cloud.
def customCallback(client, userdata, message):
    jsonState = json.loads(message.payload)
    state = jsonState ['state']
    desired = state ['desired']
    switch = desired['switch']


    if switch == "off":
        print ("  ")
        print ("  ")
        print ("*******************************************************************")
        print ("Machine Learning Pricted Failure...")
        print ("Initiating system shutdwn ....\n")
        print ("System shutdown completed...")
        print ("*******************************************************************")
        print ("  ")
        print ("  ")

        global control
        control = "off"

    if switch == "on":
        print ("Activating system...\n....\n")
        time.sleep(1)
        print ("Starting to sent telemetry data to AWS IoT...\n")
        control = "on"


host = "a1fxk1hmr8421j-ats.iot.eu-west-1.amazonaws.com" #replace this with your IoT host name
rootCAPath = "AmazonRootCA1.pem" #replace this with your root CA certificate
certificatePath = "Certificato.cert.pem" #replace this with your device certificate
privateKeyPath = "Chiave.private.key" #replace this with your device private key

print (" ")
print ("*************************************")

print ("Activating system...\n")
print (" ")
time.sleep(1)
print ("Starting to sent telemetry  to AWS IoT...\n")
print ("*************************************")
print (" ")

time.sleep(2)

# Spin up resources needed by awsiot
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

#Init awsiot client
myAWSIoTMQTTClient = mqtt_connection_builder.mtls_from_path(
    endpoint=host,
    cert_filepath=certificatePath,
    pri_key_filepath=privateKeyPath,
    clean_session=False,
    ca_filepath=rootCAPath,
    client_bootstrap=client_bootstrap,
    keep_alive_secs=30,
    client_id="IoTPDC"
)

# Connect and subscribe to AWS IoT
try:
    myAWSIoTMQTTClient.connect().result()
    print("Connected to AWS IoT")
except:
    print("Error connecting to AWS IoT")
    exit(1)

# Here we subscribe to the device shadow topic, and specify the function 'customCallback' when shadow is updated
# replace the shadow update topic with your own device topic - you can find this on IoT console.
try:
    subscribe_future, _ = myAWSIoTMQTTClient.subscribe(
        topic="$aws/things/iotpdc/shadow/update",
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=customCallback
    )
    subscribe_result = subscribe_future.result()
    print ("Subscribed with {QOS} to {topic}".format(QOS=str(subscribe_result['qos']), topic=str(subscribe_result['topic'])))
except:
    print("Error subscribing to Topic")
    exit(1)

#Now we go in a loop and generate simulated telemetry to send over the AWS IoT platform

while True:
    #telemetry will be sent ever one seconds so we pause the program for 2 seconds in each loop
    time.sleep (1)

    # we use variable control to check if it is set to "on", then only proceed with sending the telemetry,
    # in case it is "off" we will not.
    # this variable is switched to "off" in the customeCallback function above,
    # when device recives a message to stop the device.

    if control == "on":
        #randomly generating data....

        timestamp = str (datetime.datetime.now())
        product_id = randint(1,10)

        temp = randint(30,85)
        humid = randint(30,70)

        latitude = 52.160594
        longitude = -0.5997986
        location = str(randint(1,100))

        if product_id == 1:
            latitude = 52.160594
            longitude = -0.5997986

        if product_id == 2:
            latitude = 32.983310
            longitude = -78.954046

        if product_id == 3:
            latitude = 27.895177
            longitude = -95.218242

        if product_id == 4:
            latitude = 41.146755
            longitude = -114.922116

        if product_id == 5:
            latitude = -13.210523
            longitude = -37.987795

        if product_id == 6:
            latitude = 41.186435
            longitude = 1.994413


        #randomly generate geo_location
        geo_location = '51.70015' + location + ', -0.5997986'
        print ("----------------------------------------------------------------------------------------------------------------")
        #print ("Time: " + timestamp + " geo_location: " + str(geo_location) + " temperature: " + str(temperature) + " humidity: " + str(humidity) + " latitude: " + str(latitude) + " longitude: " + str(longitude)

        jpayload = {}

        #prepare json payload for IoT
        jpayload ['timestamp'] = timestamp
        jpayload ['geo_location'] = geo_location
        jpayload ['temperature'] = int(temp)
        jpayload ['humidity'] = int(humid)
        jpayload ['latitude'] = latitude
        jpayload ['longitude'] = longitude


        json_data = json.dumps(jpayload)

        print (json_data)
        print ("\n")

        # now publish to the topic...
        try:
            publish_future, _ = myAWSIoTMQTTClient.publish(
                topic = "iotpdc/telemetry",
                payload = json_data,
                qos = mqtt.QoS.AT_LEAST_ONCE
            )
            publish_future.result()
        except:
            print ("Error publishing data to AWS IoT")
