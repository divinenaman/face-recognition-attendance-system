from paho.mqtt import client as mqtt_client
import json

def connect_mqtt():
    
    broker = 'mqtt.eclipseprojects.io'
    client_id = f'python-mqtt-fras'
    # username = 'emqx'
    # password = 'public'
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker)
    client.loop_start()
    return client


def publish(client, topic_id, data):
    topic = f"/mqtt/fras/{topic_id}"

    msg = {
        "room_id": data["room_id"]
    }

    result = client.publish(topic, json.dumps(msg))
    status = result[0]

    if status == 0:
        print(f"MQTT: Message Sent to topic `{topic_id}`")
    else:
        print(f"MQTT: Failed to send message to topic {topic_id}")