import json
import sys
from threading import Thread
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.clock import mainthread
from kivy.uix.popup import Popup
import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.0.254"
SUB_TOPIC = "esp/response"
PUB_TOPIC = "esp/request"

Window.size = (400, 180)


class Application(BoxLayout):

    temp = ObjectProperty(None)
    hum = ObjectProperty(None)
    status = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, 1883, 60)

        thread = Thread(target=self.mqtt_thread)
        thread.start()

    def mqtt_thread(self):
        print("Listening forever")
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        if msg.topic != SUB_TOPIC:
            return
        res = msg.payload
        try:
            res = json.loads(res)
            temp = res["temp"]
            hum = res["hum"]
            self.temp.text = "{}°C".format(temp)
            self.hum.text = "{}%".format(hum)
            self.status.color = (0, 1, 0, 1)
            self.status.text = "Success"
        except:
            self.status.color = (1, 0, 0, 1)
            self.status.text = "Error"
            return

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(SUB_TOPIC)

    def gather_data(self):
        # request both metrics, JSON array payload
        self.client.publish(PUB_TOPIC, '["temp", "hum"]')
        self.status.color = (1, 1, 0, 1)
        self.status.text = "Request sent"


class NodeMcuApp(App):
    def build(self):
        return Application()


print("Starting app")
if __name__ == "__main__":
    NodeMcuApp().run()
