import time
from pyModbusTCP.client import ModbusClient

client = ModbusClient(host='192.168.1.80', port=502)
connection_ok = client.open()
if not connection_ok:
    print('[ERROR] Could not connect to host.')


# Sensors
AT_ENTRY_1 = 0
AT_ENTRY_2 = 1
AT_TRANSFER_1 = 2
AT_TRANSFER_2 = 3
AT_EXIT = 4

# Console buttons
BUTTON_START = 5
BUTTON_RESET = 6
BUTTON_STOP = 7
BUTTON_EMERGENCY_STOP = 8
BUTTTON_AUTO = 9

# Actuators
CONVEYOR_1 = 0
CONVEYOR_2 = 5
LOAD_1 = 1
LOAD_2 = 6
TRANSFER_LEFT_1 = 4
TRANSFER_LEFT_2 = 9
actuators = [CONVEYOR_1, CONVEYOR_2, LOAD_1, LOAD_2, TRANSFER_LEFT_1, TRANSFER_LEFT_2]
conveyors = [CONVEYOR_1, CONVEYOR_2]
loaders = [LOAD_1, LOAD_2]
transfers = [TRANSFER_LEFT_1, TRANSFER_LEFT_2]

# Status lights
LIGHT_START = 11
LIGHT_RESET = 12
LIGHT_STOP = 13
lights = [LIGHT_START, LIGHT_RESET, LIGHT_STOP]

# Console counter
COUNTER = 0


# Factory setup
counter = 0
previous_exit_state = False
client.write_single_register(COUNTER, counter)
for light in lights:
    client.write_single_coil(light, False)
for actuator in actuators:
    client.write_single_coil(actuator, False)
for conveyor in conveyors:
    client.write_single_coil(conveyor, True)
for loader in loaders:
    client.write_single_coil(loader, True)

while True:
    time.sleep(0.2)

    # When pallet is on loader 2, turn off entry conveyor 2 and loader 2
    if client.read_discrete_inputs(AT_TRANSFER_2)[0]:
        client.write_single_coil(LOAD_2, False)

    # If there is a pallet on loader 2 (or it is being moved) and another one is arriving, stop it before loader 2
    if (client.read_discrete_inputs(AT_TRANSFER_2)[0] or client.read_coils(TRANSFER_LEFT_2)[0]) and client.read_discrete_inputs(AT_ENTRY_2)[0]:
        client.write_single_coil(CONVEYOR_2, False)

    # If a pallet is being transfered, stop conveyor 1 just before entering the loader
    if (client.read_coils(TRANSFER_LEFT_1)[0] or client.read_coils(TRANSFER_LEFT_2)[0]) and client.read_discrete_inputs(AT_ENTRY_1)[0]:
        client.write_single_coil(CONVEYOR_1, False)

    # If a pallet is waiting on loader 2 and the way is clear, move it right
    if client.read_discrete_inputs(AT_TRANSFER_2)[0] and (not client.read_discrete_inputs(TRANSFER_LEFT_1)[0] and not client.read_discrete_inputs(AT_EXIT)[0]) and not client.read_discrete_inputs(AT_ENTRY_1)[0]:
        for transfer in transfers:
            client.write_single_coil(transfer, True)
        
    # Once the pallet has been merged, make it go forward
    if client.read_discrete_inputs(AT_TRANSFER_1)[0]:
        for transfer in transfers:
            client.write_single_coil(transfer, False)
        for loader in loaders:
            client.write_single_coil(loader, True)
    if client.read_discrete_inputs(AT_TRANSFER_1)[0] and client.read_discrete_inputs(AT_EXIT)[0] and not client.read_discrete_inputs(AT_TRANSFER_2)[0]:
        for conveyor in conveyors:
            client.write_single_coil(conveyor, True)

    # Offload pallet from loader 1
    if client.read_discrete_inputs(AT_EXIT)[0] and not client.read_discrete_inputs(TRANSFER_LEFT_1)[0]:
        client.write_single_coil(LOAD_1, False)

    # Update pallet counter
    if not previous_exit_state and client.read_discrete_inputs(AT_EXIT)[0]:
        counter += 1

    # Reset counter if reset button is pressed
    if client.read_discrete_inputs(BUTTON_RESET)[0]:
        client.write_single_coil(LIGHT_RESET, True)
        counter = 0
    if not client.read_discrete_inputs(BUTTON_RESET)[0]:
        client.write_single_coil(LIGHT_RESET, False)

    client.write_single_register(COUNTER, counter)
    previous_exit_state = client.read_discrete_inputs(AT_EXIT)[0]
