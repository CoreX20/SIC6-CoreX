from machine import Pin
from umqtt.simple import MQTTClient
import ujson
import network
import utime as time
import dht
import urequests as requests

DEVICE_ID = "sic6corex"
WIFI_SSID = "Casablanca 2.4"
WIFI_PASSWORD = "61174desamenganti"
MQTT_BROKER = "sic6sparks.shiftr.io"
MQTT_CLIENT = DEVICE_ID
MQTT_TELEMETRY_TOPIC = "iot/telemetry"
MQTT_CONTROL_TOPIC = "iot/control"
TOKEN = "BBUS-yzTeYERqDXIbREp17mfFoVvraflJiv"
DHT_PIN = Pin(5)

def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

def create_json_data(temperature, humidity):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "type": "sensor"
    })
    return data

def mqtt_client_publish(topic, data):
    print("\nUpdating MQTT Broker...")
    mqtt_client.publish(topic, data)
    print(data)

def send_data(temperature, humidity):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
    }
    response = requests.post(url, json=data, headers=headers)
    print("Done Sending Data!")
    print("Response:", response.text)

wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi", end="")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("WiFi Connected!")
print(wifi_client.ifconfig())

dht_sensor = dht.DHT11(DHT_PIN)
telemetry_data_old = ""

while True:
    try:
        dht_sensor.measure()
    except:
        pass

    time.sleep(0.25)

    telemetry_data_new = create_json_data(dht_sensor.temperature(), dht_sensor.humidity())

    if telemetry_data_new != telemetry_data_old:
        telemetry_data_old = telemetry_data_new
        
        # Call the send_data function to send data to Ubidots
        send_data(dht_sensor.temperature(), dht_sensor.humidity())
    
    time.sleep(0.25)
