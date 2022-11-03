from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import get_2comp
import time

client = ModbusClient(host='192.168.1.80', port=502)
connection_ok = client.open()
if not connection_ok:
    print('[ERROR] Could not connect to host.')

SENSOR_A = 0
SENSOR_B = 1
CONVEYOR = 0
CONVEYOR_SPEED = 700

# Reset conveyor when driver starts
client.write_single_register(CONVEYOR, 0)

while(True):
    time.sleep(0.1)

    if not client.read_discrete_inputs(SENSOR_A)[0]:
        client.write_single_register(CONVEYOR, get_2comp(CONVEYOR_SPEED))

    if not client.read_discrete_inputs(SENSOR_B)[0]:
        client.write_single_register(CONVEYOR, get_2comp(-CONVEYOR_SPEED))
