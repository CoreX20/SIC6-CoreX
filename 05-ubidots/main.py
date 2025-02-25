from machine import Pin

# from umqtt.simple import MQTTClient
# import ujson
import network
import utime as time
import dht
import urequests as requests

DEVICE_ID = "sic6corex"
WIFI_SSID = "Casablanca 2.4"
WIFI_PASSWORD = "61174desamenganti"
# MQTT_BROKER = "sic6sparks.shiftr.io"
# MQTT_CLIENT = DEVICE_ID
# MQTT_TELEMETRY_TOPIC = "iot/telemetry"
# MQTT_CONTROL_TOPIC = "iot/control"
TOKEN = "BBUS-yzTeYERqDXIbREp17mfFoVvraflJiv"
DHT_PIN = Pin(5)
dht_sensor = dht.DHT11(DHT_PIN)
pir_sensor = Pin(2, Pin.IN)

server_url = "http://192.168.1.8:5000/sensor_data"  # Ubah sesuai Flask server IP address

# def did_receive_callback(topic, message):
#     print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

# def create_json_data(temperature, humidity):
#     data = ujson.dumps({
#         "device_id": DEVICE_ID,
#         "temp": temperature,
#         "humidity": humidity,
#         "type": "sensor"
#     })
#     return data


# def mqtt_client_publish(topic, data):
#     print("\nUpdating MQTT Broker...")
#     mqtt_client.publish(topic, data)
#     print(data)


def read_dht_data():
    try:
        dht_sensor.measure()
        humidity = dht_sensor.humidity()
        temperature = dht_sensor.temperature()
        return humidity, temperature
    except Exception as e:
        print(f"Error reading DHT sensor: {e}")
        return None, None


def read_pir_data():
    try:
        return pir_sensor.value()
    except Exception as e:
        print(f"Error reading PIR sensor: {e}")
        return None


def send_data_to_ubidots(temperature, humidity, motion):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {"temp": temperature, "humidity": humidity, "motion": motion}
    response = requests.post(url, json=data, headers=headers)

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print("Data sent successfully to Ubidots!")
        else:
            print(f"Error sending data to Ubidots. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to Ubidots: {e}")


def send_data_to_flask(sensor_type, sensor_id, sensor_data):
    data = {"sensor_id": sensor_id, "sensor_type": sensor_type, "value": sensor_data}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(server_url, json=data, headers=headers)
        print("Response from Flask:", response.json())
    except Exception as e:
        print("Failed to send data to Flask:", e)


# Wi-Fi Connection
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi", end="")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("WiFi Connected!")
print(wifi_client.ifconfig())

while True:
    humidity, temperature = read_dht_data()
    if humidity is not None and temperature is not None:
        print(f"Humidity: {humidity}% Temperature: {temperature}°C")
        dht_data = {"humidity": humidity, "temperature": temperature}
        send_data_to_flask("DHT", "dht_01", dht_data)
    else:
        print("Error reading DHT data, skipping Flask and Ubidots updates.")

    motion_detected = read_pir_data()
    if motion_detected is not None:
        print(f"Motion Detected: {motion_detected}")
        pir_data = {"motion": motion_detected}
        send_data_to_flask("PIR", "pir_01", pir_data)

    if humidity is not None and temperature is not None and motion_detected is not None:
        send_data_to_ubidots(temperature, humidity, motion_detected)

    time.sleep(2)
