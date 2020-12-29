import re
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

import json

INFLUXDB_ADDRESS = '192.168.0.167'
INFLUXDB_USER = 'feliksj'
INFLUXDB_PASSWORD = 'ThinkPadL%70'
INFLUXDB_DATABASE = 'home_assistant'

MQTT_ADDRESS = '192.168.0.167'
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = 'tests/fx2/temperatura'
MQTT_REGEX = 'tests/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


class SensorData(NamedTuple):
    data: str
    value: float


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def _parse_mqtt_message(topic, payload):
    match = re.match(MQTT_REGEX, topic)
    print(match)
    if match:
        print(payload)
        print("#################################")
        print(match)
        json_object = json.loads(payload)

        data = json_object["Data"]
        tempe = json_object["Temperatura"]

        return SensorData(data, float(tempe))
    else:
        return None


def _send_sensor_data_to_influxdb(sensor_data):
    json_body = [
        {
            "measurement": "C",
            "tags": {
                "entity_id": "temp"
            },
            "time": sensor_data.data+"T16:46:46.903327Z",
            "fields": {
                "value": sensor_data.value
            }
        }]
    influxdb_client.write_points(json_body)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    print(sensor_data)
    if sensor_data is not None:
        print("Ready to send to influxdb")
        _send_sensor_data_to_influxdb(sensor_data)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    # mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()
