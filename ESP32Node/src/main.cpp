#include <Arduino.h>
#include <WiFi.h>
#include <MyConfig.h>
#include <PubSubClient.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include "DHT.h"
#include <Adafruit_BMP085.h>
#include <SPI.h>

bool state = true;

const char *ssid = WIFI_NAME;
const char *password = WIFI_PASSWORD;

const char *mqtt_server = MQTT_SERVER_IP;

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

// Sensor readings variables
float temperature;
float humidity;
float moisture;
float pressure;
int light;

#define TEMPERATURE_PIN 4
#define DHTPIN 5
#define MOISTURE_PIN 34
#define LIGHT_PIN 35

#define LATITUDE 36.917608
#define LONGITUDE 30.615581
const int ledPin = 2;

OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature sensors(&oneWire);

DHT dht(DHTPIN, DHT11);

Adafruit_BMP085 bmp;

// Random sensor data generator
float generateRandomNumber(float start, float finish)
{
  return (float)((finish - start) * esp_random()) / UINT32_MAX;
}

// Temperature Sensor reader function
float readTemperatureSensor(bool shouldPrint)
{
  sensors.requestTemperatures();

  float tempC = sensors.getTempCByIndex(0);

  if (tempC != DEVICE_DISCONNECTED_C && shouldPrint)
  {
    Serial.print("Temperature: ");
    Serial.println(tempC);
  }

  return tempC;
}

// Humidity sensor reader function
float readHumiditySensor(bool shouldPrint)
{

  float h = dht.readHumidity();
  if (!isnan(h))
  {
    if (shouldPrint)
    {
      Serial.print(F("Humidity: "));
      Serial.println(h);
    }

    return h;
  }
  else
  {
    return (float)-2;
  }
}

// Moisture sensor reader function
float readMoistureSensor(bool shouldPrint)
{
  int adcValue = 0;

  adcValue = analogRead(MOISTURE_PIN);

  if (shouldPrint)
  {
    Serial.print("Moisture value: ");
    Serial.println(adcValue);
  }
  return adcValue;
}
int readPressureSensor(bool shouldPrint)
{
  int pressure = bmp.readPressure();
  if (shouldPrint)
  {
    Serial.print("Pressure: ");
    Serial.print(pressure);
    Serial.println(" Pa");
  }

  return pressure;
}

int readLightSensor(bool shouldPrint){
  int light = analogRead(LIGHT_PIN) <= 1000 ? 0 : 1;
  if (shouldPrint)
  {
    Serial.print("Light: ");
    Serial.println(light);
  }
  return light;
}

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
    if (client.connect(MQTT_CLIENT_ID))
    {
      Serial.println("connected");
      // Subscribe
      // client.subscribe("node/output");
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
  pinMode(ledPin, OUTPUT);
  sensors.begin();
  dht.begin();
  if (!bmp.begin())
  {
    Serial.println("Could not find a valid BMP085/BMP180 sensor, check wiring!");
    while (1)
    {
    }
  }
}

void loop()
{
  /*
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
  */
  if (state)
  {
    long now = millis();
    if (now - lastMsg > 3000)
    {
      lastMsg = now;

      // Reader sensor datas
      temperature = readTemperatureSensor(true);
      humidity = readHumiditySensor(true);
      moisture = readMoistureSensor(true);
      pressure = readPressureSensor(true);
      // temperature = generateRandomNumber(10.0f, 50.0f);
      // humidity = generateRandomNumber(10.0f, 50.0f);
      // moisture = generateRandomNumber(10.0f, 50.0f);
      // pressure = generateRandomNumber(10.0f, 50.0f);
      //light = generateRandomNumber(0.0f, 1.0f) <= 0.5f ? 0 : 1;
      light = readLightSensor(true);

      // Concatenating sensor readings
      char strToSend[100];
      snprintf(strToSend, 100, "%s;%.2f;%.2f;%.2f;%d;%d;%.6f;%.6f", MQTT_CLIENT_ID, temperature, humidity, moisture, pressure, light, LATITUDE, LONGITUDE);

      Serial.print("Message sent: ");
      Serial.println(strToSend);
      Serial.println(MQTT_NODE_TOPIC);
      client.publish(MQTT_NODE_TOPIC, strToSend);
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