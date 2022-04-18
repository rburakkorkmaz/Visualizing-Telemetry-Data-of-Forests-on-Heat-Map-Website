"""
	Author: Ramazan Burak Korkmaz
	Date: 18.04.2022
	This python script is responsible from controling and gathering
	sensordata informations from ESP32 nodes (slaves) by MQTT protocol.

	First argument ----> IP ADDRESS (default: RPI Local IP Address)
	Second argument ---> MQTT topic of sensordata (default: node/sensor_data)
	Third argument ----> MQTT topic of ESP32 ON/OFF control (default: node/state)
"""

import paho.mqtt.client as mqtt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--IP_ADDRESS", help="IP Address used for MQTT client (default: RPI Local IP Address)", required = False)
parser.add_argument("--MQTT_SENSOR_DATA_TOPIC", help = "MQTT topic to subscribe for sensor data from ESP32 node (default: node/sensor_data)", required = False)
parser.add_argument("--MQTT_ESP32_STATE_TOPIC", help = "MQTT topic to control ESP32 ON/OFF state (default: node/state)", required = False)
args = parser.parse_args()


# Some variables
client_IP_address = args.IP_ADDRESS if args.IP_ADDRESS else "192.168.1.34"
sensor_data_topic = args.MQTT_SENSOR_DATA_TOPIC if args.MQTT_SENSOR_DATA_TOPIC else "node/sensor_data"
ESP32_state_topic = args.MQTT_ESP32_STATE_TOPIC if args.MQTT_ESP32_STATE_TOPIC else  "node/state"


print(f"Client IP: {client_IP_address}")
print(f"Data Topic: {sensor_data_topic}")
print(f"State topic: {ESP32_state_topic}")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("testTopic")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message

# Connect to the given IP address
client.connect("192.168.1.34", 1883, 60)

# Loop forever
client.loop_forever()
