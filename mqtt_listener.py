import paho.mqtt.client as mqtt
import json
import os
import time
from dotenv import load_dotenv
#import streamlit as st
import requests
import time
load_dotenv()
BROKER = "192.168.1.6"
PORT = 1883
TOPIC = "lab/sensor"

# =========================================================
# THINGSPEAK CONFIG
# =========================================================

THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY")

THINGSPEAK_URL = (
    "https://api.thingspeak.com/update"
)

os.makedirs("data", exist_ok=True)

DATA_FILE = "data/live_sensor.json"

# =========================================================
# SEND TO THINGSPEAK
# =========================================================

def send_to_thingspeak(

    temperature,
    humidity

):

    try:

        payload = {

            "api_key": THINGSPEAK_API_KEY,

            "field1": temperature,

            "field2": humidity
        }

        response = requests.get(

            THINGSPEAK_URL,

            params=payload,

            timeout=5
        )

        print(
            "ThingSpeak Upload:",
            response.status_code
        )

    except Exception as e:

        print(
            "ThingSpeak Error:",
            e
        )

def on_connect(client, userdata, flags, rc):

    print("MQTT Connected")

    client.subscribe("lab/sensor",qos=0)
    print("Susbcribed to lab/sensor")
def on_message(client, userdata, msg):

    try:

        payload = msg.payload.decode()

        print("MQTT RECEIVED:", payload)

        temp, hum = payload.split(",")

        data = {
            "temperature": float(temp),
            "humidity": float(hum)
        }

        with open(DATA_FILE, "w") as f:

            json.dump(data, f)
            send_to_thingspeak(

    float(temp),
    float(hum)
)

    except Exception as e:

        print("Error:", e)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("STARTING MQTT LOOP")
client.loop_forever()