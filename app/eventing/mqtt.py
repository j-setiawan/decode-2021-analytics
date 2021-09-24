import certifi
import paho.mqtt.client as mqtt


class MqttClient:
    # Callback on connection
    def on_connect(self, client, userdata, flags, rc):
        print(f'Connected (Result: {rc})')
        self.client.subscribe('#')

    def __init__(self, hostname, username, password, on_message):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = on_message
        self.client.tls_set(ca_certs=certifi.where())
        self.client.username_pw_set(username, password)
        self.client.connect(hostname, port=8883)
        self.client.loop_start()
