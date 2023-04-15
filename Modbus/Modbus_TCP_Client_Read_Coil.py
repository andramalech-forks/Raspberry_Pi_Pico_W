import time
from umodbus.tcp import TCP as ModbusTCPMaster
import network

# ===============================================
# connect to a network
station = network.WLAN(network.STA_IF)
if station.active() and station.isconnected():
    station.disconnect()
    time.sleep(1)
station.active(False)
time.sleep(1)
station.active(True)

# station.connect('SSID', 'PASSWORD')
station.connect('Fusion Automate', 'Fusion_Automate')
time.sleep(1)

while True:
    print('Waiting for WiFi connection...')
    if station.isconnected():
        print('Connected to WiFi.')
        print(station.ifconfig())
        break
    time.sleep(2)
# ===============================================
# TCP Slave setup
port = 502            # port to listen to
slave_addr = 1        # bus address of modbus_client
coil_address = 0      # Starting Coil Address
coil_qty = 10         # Number of Coils to Read in Single Request

# IP Address of Modbus TCP Server
ip = '192.168.29.221'

# Setup Modbus TCP Client
modbus_client = ModbusTCPMaster(slave_ip=ip,slave_port=port,timeout=5)
print(f'Updating data to Modbus TCP Server at {ip}:{port}')
       
# READ COILS
coil_status = modbus_client.read_coils(slave_addr=slave_addr,starting_addr=coil_address,coil_qty=coil_qty)
print('Status of COIL from {} to {} : {}'.format(coil_address, coil_address + coil_qty, coil_status))
