import time
import board
import analogio

# Set A1 for receving data from the light sensor module
light = analogio.AnalogIn(board.A0)

while True:
    if light.value < 15000:
        print ("LED OFF")
    else:
        print ("LED ON")
    print (light.value)
    time.sleep(0.1)