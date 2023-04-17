from umodbus.tcp import ModbusTCP
from umqtt.simple import MQTTClient
import time
from machine import Pin
import network

myLED = Pin('LED',Pin.OUT)
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
        print(f'Connected to WiFi, Pico W IP : {station.ifconfig()[0]}')
        break
    time.sleep(2)
# ===============================================
# Define MQTT Broker credentials
MQTT_BROKER_IP = '192.168.29.221'
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = 'Pico_W_Mqtt_Client'
MQTT_TOPIC = 'Pico_W/Modbus'

# Define MQTT client
mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER_IP, MQTT_BROKER_PORT,keepalive=30)
mqtt_client.connect()

tcp_port = 502
local_ip = station.ifconfig()[0]

# ModbusTCP can get TCP requests from a host device to provide/set data
client = ModbusTCP()
is_bound = False

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()

if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)

def LED_cb(reg_type, address, val):
    print(reg_type, address, val)
    print(MQTT_TOPIC+"/"+str(reg_type)+" - "+str(address))
    mqtt_client.publish(MQTT_TOPIC+"/"+str(reg_type)+" - "+str(address), str(val))
    if int(val[0]) == 1:myLED.on()
    elif int(val[0]) == 0:myLED.off()
    else: pass

# commond slave register setup, to be used with the Master example above
register_definitions = {
'ISTS': {'EXAMPLE_ISTS': {'val': 0, 'register': 0, 'len': 1}},
'IREGS': {'EXAMPLE_IREG1': {'val': 0, 'register': 0, 'len': 1},
          'EXAMPLE_IREG2': {'val': 0, 'register': 1, 'len': 1}},
'HREGS': {'EXAMPLE_HREG2': {'val': 0, 'register': 0, 'len': 1},
          'EXAMPLE_HREG1': {'val': 0, 'register': 1, 'len': 1}},
'COILS': {'EXAMPLE_COIL1': {'val': 0, 'register': 0, 'len': 1},
          'EXAMPLE_COIL2': {'val': 0, 'register': 1, 'len': 1}}
}

#register_definitions['COILS']['LED']['on_set_cb'] = LED_cb
#register_definitions['COILS']['EXAMPLE_COIL1']['on_get_cb'] = LED_cb
#register_definitions['COILS']['EXAMPLE_COIL2']['on_get_cb'] = LED_cb
register_definitions['HREGS']['EXAMPLE_HREG1']['on_get_cb'] = LED_cb
register_definitions['HREGS']['EXAMPLE_HREG2']['on_get_cb'] = LED_cb
#register_definitions['IREGS']['EXAMPLE_IREG1']['on_get_cb'] = LED_cb
#register_definitions['IREGS']['EXAMPLE_IREG2']['on_get_cb'] = LED_cb
#register_definitions['ISTS']['EXAMPLE_ISTS']['on_get_cb'] = LED_cb


print('Setting up registers ...')
client.setup_registers(registers=register_definitions)
print('Register setup done')
print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")

