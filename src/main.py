# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import threading
from new_state_machine import *
from pymodbus import Framer
from pymodbus.client import ModbusSerialClient
from socket_tcp import *
from src.commands_parse import execute_command
from share_variables import *
from remote_control_IO import io_relay_controller
from remote_control_alarm import ModbusAlarm
from remote_detect_current import current_detector
import yaml


def io_controller_handler(devices, timeout, lock):
    """
    Threading function to read io input and output as well as current.
    This function run a specific amount of time periodically
    :param devices: list of devices such as current sensor, io_relays, alarm and etc
    :param timeout: the period of time between wake and sleep for this threading
    :param lock: lock for shared data structure between socket and threading
    :return:
    """

    print("io_controller_handler start")
    global RS485_devices_reading

    while True:
        with (lock):
            result = execute_command("read", devices)
            RS485_devices_reading["current"] = result[0]
            RS485_devices_reading["io_input"] = result[1]
            RS485_devices_reading["io_output"] = result[2]

        time.sleep(timeout)


def tcp_handler(server: tcp_server, timeout, lock):
    """
    predefined structure for tcp communication:
    four temperature's data: four float variables;
    conveyor status: bool; robot status: bool; system commands, start
    and stop : bool;
    {
        temperatures : [T11,T12,T21,T22],
        conveyor: bool, status of conveyor
        robot: bool, status of robot
        start: bool, start command
        stop: bool, stop command
        pause: bool, pause command
    }
    :param server: pass the customized tcp server instance
    :param timeout: the period of time between wake and sleep for this threading
    :param lock: lock for shared data structure between socket and threading
    :return:
    """
    global tcp_data
    global RS485_devices_reading
    global ui_commands
    global tcp_read_json_information
    while True:
        with lock:
            tcp_data = server.read_from_client()
            if tcp_data is not None:
                tcp_read_json_information["conveyor_state"] = tcp_data["conveyor"]
                tcp_read_json_information["robot"] = tcp_data["robot"]
                tcp_read_json_information["temperature_sensors"] = tcp_data["temperature"]
                ui_commands["start_signal"] = tcp_data["start"]
                ui_commands["pause_signal"] = tcp_data["pause"]
                ui_commands["shutdown_signal"] = tcp_data["stop"]
        time.sleep(timeout)


def cv_status_monitor_handler(server: tcp_server, timeout, lock):
    """
    check rs485 devices as well as cv system
    :param server:
    :param timeout:
    :param lock:
    :return:
    """
    while True:
        with lock:
            temp = 1
        time.sleep(timeout)


def device_init():
    """
    initialize ttyUSB port and devices based on RS485_config and devices yaml file respectively.
    Meanwhile, the failure_reading and data_reading variables are initialized.
    Nevertheless, the devices' connections are checked based on if reading holding registers are successful or not
    :return: a list of devices if port and devices' instances can be created. Otherwise, None is returned
    """
    global state_variable
    global RS485_devices_reading
    global read_failure_times
    global devices_connection_flag
    devices = {}
    configs = None
    config_path = '../config/RS485_config.yaml'
    try:
        configs = load_configuration(config_path)
    except Exception as e:
        print(e)
        return devices
    port_config = configs["port"][0]
    if port_config["connection"]:
        serial_client = ModbusSerialClient(**port_config)
        connection = serial_client.connect()
        config_path = '../config/devices.yaml'
        if connection:
            try:
                configs = load_configuration(config_path)
            except Exception as e:
                print(e)
                return devices
            state_variable["port_connection_flag"] = True
            devices_config = configs["devices"]
            for spec in devices_config:
                device_type = spec.pop('type')
                if device_type == 'alarm':
                    devices[spec["name"]] = (ModbusAlarm(serial_client=serial_client,
                                                         name=spec["name"], unit=spec["unit"]))
                elif device_type == 'relays':
                    devices[spec["name"]] = (io_relay_controller(serial_client=serial_client,
                                                                 name=spec["name"], unit=spec["unit"],
                                                                 small_port=spec["small_port"]))
                elif device_type == 'current_sensor':
                    devices[spec["name"]] = (current_detector(serial_client=serial_client,
                                                              name=spec["name"], unit=spec["unit"]))
                '''
                init a dict to maintain device read data, continuously failure read times and connection flag
                check device connection, check 10 times to do connection with all devices
                '''
                devices_read = configs["devices_read"]
                for device in devices_read:
                    if device in devices.keys():
                        RS485_devices_reading[device] = None
                        read_failure_times[device] = 0
                for device in devices:
                    devices_connection_flag[device] = False
                execute_command("check", devices)
        else:
            state_variable["port_connection_flag"] = False
            print("port_connection problem")
    return devices


def socket_tcp_init():
    """
    Based on the socket_config.yaml to create a tcp connection
    :return: successful connection return socket instance, otherwise None
    """
    global state_variable
    socket_server = None
    config_path = '../config/socket_config.yaml'
    configs = None
    try:
        configs = load_configuration(config_path)
        configs = configs["tcp"][0]
    except Exception as e:
        state_variable["socket_connection_flag"] = False
        print(e)
        return None
    try:
        if configs["connection"]:
            socket_server = tcp_server(host=configs["host"], port=configs["port"],
                                       time_out=configs["connection_time_out"])
            state_variable["socket_connection_flag"] = socket_server.connect_client(
                waiting_time_out=configs["waiting_time_out"])
        else:
            state_variable["socket_connection_flag"] = True
    except Exception as e:
        print(e)
        state_variable["socket_connection_flag"] = False
    return socket_server


def control_system_run():
    """
    prepare devices and tcp socket connection. Then launch two thread to update readings from
    devices and tcp socket. Besides, a finite state machine is launched and it read devices' data
    and tcp information to execute with a set of rules
    :return:
    """
    global state_variable
    threads = []
    lock = threading.Lock()  # lock for shared data structure between socket and threading

    devices = device_init()
    if devices:
        thread = threading.Thread(target=io_controller_handler, args=(devices, 0.1, lock))
        thread.start()
        threads.append(thread)

    socket_server = socket_tcp_init()
    if socket_server:
        thread = threading.Thread(target=tcp_handler, args=(socket_server, 0.1, lock))
        thread.start()
        threads.append(thread)

    '''
    Ready to run exception monitor system and read io and tcp devices 
    '''
    print(f"RS485_devices_reading{RS485_devices_reading}")
    print(f"devices_connection_flag{devices_connection_flag}")
    print(f"read_failure_times{read_failure_times}")
    print(f"tcp_information{tcp_read_json_information}")
    print(f"ui_commands{ui_commands}")
    for key,val in state_variable.items():
        print(f"{key}:{val}")
    exception_handler_system = StateMachine(system_start_state(), lock, devices, sleep_time=1)
    exception_handler_system.run()
    # for thread in threads:
    #     thread.join()


if __name__ == '__main__':
    control_system_run()
