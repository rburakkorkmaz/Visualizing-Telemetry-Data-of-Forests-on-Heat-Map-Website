"""
	Author: Ramazan Burak Korkmaz
	Date: 18.04.2022
	This python script is responsible from controling and gathering
	sensordata informations from ESP32 nodes (slaves) by MQTT protocol.
"""

import paho.mqtt.client as mqtt
import ssl
import argparse
import json
import time
from datetime import datetime
import config.aws_mqtt_config as AWS_CONFIG


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
    return data_json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    client_id = client._client_id.decode('utf-8')
    print(f"Client: {client_id}")
    # Subscribe data topic
    if client_id == "AWS_CLIENT":
       client.subscribe("AWS_CONTROL")
    else:
       client.subscribe(sensor_data_topic + "_" + client_id)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global clients


    topic = msg.topic
    message = str(msg.payload, 'utf-8')
    client_id = str(client._client_id,'utf-8')
    #print(f"Topic: {topic}")
    #print(f"Message: {message}")
    if client_id == "AWS_CLIENT":
       message_arr = message.split(';')
       print("Toggling: ", end="")
       for node in message_arr:
          clients[node]["State"] = not clients[node]["State"]
          print(f"{node}")
    elif clients[client_id]["State"]:
       aws_send_json = convert_to_json(message, client_id)
       aws_client.publish("AWS_DATA", aws_send_json)


# The disconnect callback for slaves.
def on_disconnect(client, userdata, rc):
    global clients
    clients[client] = not clients[client]


# AWS IoT Core MQTT Client
aws_client = mqtt.Client("AWS_CLIENT", protocol=mqtt.MQTTv31)
aws_client.tls_set(AWS_CONFIG.ROOT_CA,
                   certfile = AWS_CONFIG.PUBLIC_CRT,
                   keyfile = AWS_CONFIG.PRIVATE_KEY,
                   cert_reqs = ssl.CERT_REQUIRED,
                   tls_version = ssl.PROTOCOL_TLSv1_2,
                   ciphers = None)


aws_client.on_connect = on_connect
aws_client.on_message = on_message
aws_client.connect(AWS_CONFIG.MQTT_URL, port=8883, keepalive=60)
aws_client.loop_start()

clients = {}
for i in range(1, int(args.NUMBER_OF_SLAVES)+1):
   clients[f"node_{i}"] = {"Client":mqtt.Client(f"node_{i}",protocol=mqtt.MQTTv31),
                           "State": True} 

for client in clients.values():
   #print(client._client_id)
   client["Client"].on_connect = on_connect
   client["Client"].on_message = on_message
   client["Client"].on_disconnect = on_disconnect
   # Connect to the given IP address
   client["Client"].connect("192.168.1.34", 1883, 60)

   # Loop forever
   client["Client"].loop_start()


while True:
    print("Code RUNNING")
    # aws_client.publish("testTopic", "deneme")
    print(clients)
    time.sleep(5)
