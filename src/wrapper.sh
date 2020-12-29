#!/bin/bash

sleep 60                      # Give the system time after a reboot to connect to WiFi before continuing

MY_PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python3 $MY_PWD/MQTTInfluxDBBridge.py
