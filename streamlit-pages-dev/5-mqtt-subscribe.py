import streamlit as st
import paho.mqtt.client as mqtt
import datetime

# https://www.hivemq.com/demos/websocket-client/
# set topic to testtopic/industrial-assistance

def on_connect(mqttc, obj, flags, reason_code, properties):
    print("reason_code: " + str(reason_code))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    st.write("Sensorwert:", msg.payload.decode("utf-8"))
    
def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))
    
def on_log(mqttc, obj, level, string):
    print(string)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log

mqttc.connect("broker.hivemq.com", 1883, 60)

mqttc.subscribe("testtopic/industrial-assistance")

mqttc.loop_forever()