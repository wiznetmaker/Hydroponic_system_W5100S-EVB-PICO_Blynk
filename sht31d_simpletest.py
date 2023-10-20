# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_sht31d
import digitalio

# Create sensor object, communicating over the board's default I2C bus
i2c = busio.I2C(board.GP1, board.GP0)
sensor = adafruit_sht31d.SHT31D(i2c)

heater = digitalio.DigitalInOut(board.GP2)
heater.direction = digitalio.Direction.OUTPUT

while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    if sensor.temperature < 26:
        heater.value = 1
    elif sensor.temperature >= 26:
        heater.value = 0
    time.sleep(2)

