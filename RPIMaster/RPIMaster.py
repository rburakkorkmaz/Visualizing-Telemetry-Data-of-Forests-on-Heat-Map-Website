"""
	Author: Ramazan Burak Korkmaz
	Date: 18.04.2022
	This python script is responsible from controling and gathering
	sensordata informations from ESP32 nodes (slaves) by MQTT protocol.
"""

import paho.mqtt.client as mqtt
import argparse
import json
import time
from datetime import datetime

# Argparse package usage
parser = argparse.ArgumentParser()
parser.add_argument("--IP_ADDRESS", help="IP Address used for MQTT client (default: RPI Local IP Address)")
parser.add_argument("--MQTT_SENSOR_DATA_TOPIC", help = "MQTT topic to subscribe for sensor data from ESP32 node (default: node/sensor_data)")
parser.add_argument("--MQTT_ESP32_STATE_TOPIC", help = "MQTT topic to control ESP32 ON/OFF state (default: node/state)")
parser.add_argument("NUMBER_OF_SLAVES", help = "Number of ESP32s connect to RPI (Limit: 20)")
args = parser.parse_args()
if int(args.NUMBER_OF_SLAVES) > 20:
   parser.error("Slave limit exceeded")


# Variables change according to argument parsed by user
client_IP_address = args.IP_ADDRESS if args.IP_ADDRESS else "192.168.1.34"
sensor_data_topic = args.MQTT_SENSOR_DATA_TOPIC if args.MQTT_SENSOR_DATA_TOPIC else "node/sensor_data"
ESP32_state_topic = args.MQTT_ESP32_STATE_TOPIC if args.MQTT_ESP32_STATE_TOPIC else  "node/state"

# Print settings at the start of script
print(f"Client IP: {client_IP_address}")
print(f"Data Topic: {sensor_data_topic + '_node_i'}")
print(f"State topic: {ESP32_state_topic + '_node_i'}")
print(f"Number of clients: {args.NUMBER_OF_SLAVES}")


def convert_to_json(data: str, client_id: str)-> json:
    # Split string with string ;
    splited_data = data.split(";")
    
    # Creating a dictionary so I can easily convert it to json
    temp = {
         client_id: {
                  "Temperature": splited_data[0],
                  "Humidity": splited_data[1],
                  "Moisture": splited_data[2],
                  "Pressure": splited_data[3],
	          "Light": splited_data[4],
                  "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         }
    }

    data_json = json.dumps(temp)
    print(data_json)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #print(f"Client: {client._client_id}")
    
    client_id = client._client_id.decode('utf-8')
    # Subscribe data topic
    client.subscribe(sensor_data_topic + "_" + client_id)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode('utf-8')
    client_id = client._client_id.decode('utf-8')

    print(f"Topic: {topic}")
    print(f"Message: {message}")

    convert_to_json(message, client_id)

clients = []
for i in range(0, int(args.NUMBER_OF_SLAVES)):
   clients.append(mqtt.Client(f"node_{i}",protocol=mqtt.MQTTv31))

for client in clients:
   #print(client._client_id)
   client.on_connect = on_connect
   client.on_message = on_message

   # Connect to the given IP address
   client.connect("192.168.1.34", 1883, 60)

   # Loop forever
   client.loop_start()


while True:
    print("Code RUNNING")
    time.sleep(5)
