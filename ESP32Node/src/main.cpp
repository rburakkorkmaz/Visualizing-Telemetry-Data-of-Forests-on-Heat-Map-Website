#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "DHT.h"

bool state = true;

const char *ssid = "*"";
const char *password = "*";

const char *mqtt_server = "*";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

#define DHTPIN 4
#define DHTTYPE DHT11

const int ledPin = 2;

DHT dht(DHTPIN, DHTTYPE);

void setup_wifi()
{
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *message, unsigned int length)
{
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;

  for (int i = 0; i < length; i++)
  {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  // If a message is received on the topic esp32/output, you check if the message is either "on" or "off".
  // Changes the output state according to the message
  if (String(topic) == "node/output")
  {
    Serial.print("Changing output to ");
    if (messageTemp == "on")
    {
      Serial.println("on");
      state = true;
      digitalWrite(ledPin, HIGH);
    }
    else if (messageTemp == "off")
    {
      Serial.println("off");
      state = false;
      digitalWrite(ledPin, LOW);
    }
  }
}

void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client"))
    {
      Serial.println("connected");
      // Subscribe
      client.subscribe("node/output");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.println(F("DHTxx test!"));
  pinMode(ledPin, OUTPUT);
  dht.begin();
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  if (state)
  {
    long now = millis();
    if (now - lastMsg > 1000)
    {
      lastMsg = now;

      // Temperature in Celsius
      float h = dht.readHumidity();

      // Convert the value to a char array
      char tempString[8];
      dtostrf(h, 1, 2, tempString);
      Serial.print(F("Humidity: "));
      Serial.println(h);

      client.publish("esp32/sensorData", tempString);
    }
  }
  else
  {
    long now = millis();
    if (now - lastMsg > 1000)
    {
      lastMsg = now;
      Serial.println("No need to collect data.");
    }
  }
}