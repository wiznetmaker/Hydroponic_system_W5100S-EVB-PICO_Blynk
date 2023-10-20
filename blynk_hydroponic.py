import board
import digitalio
import time
import busio
import struct
import BlynkLib
import adafruit_sht31d
import analogio


import adafruit_requests as requests
from adafruit_wiznet5k.adafruit_wiznet5k import * #active WIZnet chip library
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket #open socket from WIZnet library

# Go to your blynk device and input related information
BLYNK_TEMPLATE_ID =  "XXXXXXXXXXX"
BLYNK_DEVICE_NAME = "XXXXXXXXXXXXXXXXX
BLYNK_AUTH_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

i2c = busio.I2C(board.GP1, board.GP0)
sensor = adafruit_sht31d.SHT31D(i2c)

# Set A0 for receving data from the light sensor module
light = analogio.AnalogIn(board.A0)

#meter = MAX471.MAX471(voltage_pin = board.A1, current_pin = board.A2)

# Set heater
heater = digitalio.DigitalInOut(board.GP2)
heater.direction = digitalio.Direction.OUTPUT

# Set LED light
led = digitalio.DigitalInOut(board.GP3)
led.direction = digitalio.Direction.OUTPUT

# Set pump 
pump = digitalio.DigitalInOut(board.GP4)
pump.direction = digitalio.Direction.OUTPUT

# Activate GPIO pins for SPI communication
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

# Activate Reset pin for communication with W5500 chip
W5x00_RSTn = board.GP20

print("Wiznet5k SimpleServer Test (DHCP)")

class Blynk(BlynkLib.BlynkProtocol):
    def __init__(self, auth, **kwargs):
        self.insecure = kwargs.pop('insecure', True)
        self.server = kwargs.pop('server', 'blynk.cloud')
        self.port = kwargs.pop('port', 80 if self.insecure else 443)
        BlynkLib.BlynkProtocol.__init__(self, auth, **kwargs)
        #self.on('redirect', self.redirect)
    
    def _write(self, data):
        #print('<', data)
        client.send(data) #information that we send out
        # TODO: handle disconnect
    
    def run(self):
        data = b''
        try:
            data = client.recv() #information that we received from Blynk
            #print('>', data)
        except KeyboardInterrupt:
            raise
        #except socket.timeout:
            # No data received, call process to send ping messages when needed
            #pass
        except: # TODO: handle disconnect
            return
        self.process(data)


# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = (0x00, 0x08, 0xDC, 0x11, 0x22, 0x33)
IP_ADDRESS = (192, 168, 0, 111)
SUBNET_MASK = (255, 255, 0, 0)
GATEWAY_ADDRESS = (192, 168, 0, 1)
DNS_SERVER = (8, 8, 8, 8)



# Set reset function
ethernetRst = digitalio.DigitalInOut(W5x00_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

# Set this SPI for selecting the correct chip
cs = digitalio.DigitalInOut(SPI0_CSn)

# Set the GPIO pins for SPI communication
spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

# Reset WIZnet's chip first
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)

# Show all information
print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

# Initialize steps for WIZnet's socket to create TCP server
socket.set_interface(eth)
client = socket.socket()  # Set and name the socket to be a TCP server
client_ip = "128.199.144.129"  #blynk.cloud
client_port = 80  # HTTP port for Blynk Port
client.connect((client_ip, client_port), None)

blynk = Blynk(BLYNK_AUTH_TOKEN)

@blynk.on("V4")
def Pump(value):

    if value[0] == "1":
        print ("Pump is ON")
        pump.value = 1
    elif value[0] == "0":
        print ("Pump is OFF")
        pump.value = 0        

@blynk.on("V6")
def LED_light(value):

    if value[0] == "1":
        print ("LED light is ON")
        led.value = 1
    elif value[0] == "0":
        print ("LED light is OFF")
        led.value = 0
        
@blynk.on("V8")
def Heater(value):

    if value[0] == "1":
        print ("Heater is ON")
        heater.value = 1
    elif value[0] == "0":
        print ("Heater is OFF")
        heater.value = 0 

while True:
# Maintain DHCP lease (continue the DHCP setting while TCP is connected)
    eth.maintain_dhcp_lease()

    #led.value = not led.value #showing the light is blinking
    time.sleep(0.1) #transmit data speed
    

    #During the connection with Blynk Cloud, you could modified in this section.
    if client.status == SNSR_SOCK_ESTABLISHED:
        blynk.run()

        blynk.virtual_write(1, str(light.value))        
        blynk.virtual_write(0, str(sensor.temperature))
        print (sensor.temperature)   
        time.sleep(0.1)
    # Found out the connection has been disconnected from the server
    elif client.status == SNSR_SOCK_CLOSE_WAIT:
        client.disconnect() #close the connection
    # Socket has closed
    elif client.status == SNSR_SOCK_CLOSED:
        client.connect((client_ip, client_port), None)


