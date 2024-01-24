# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import threading
from new_state_machine import *
from pymodbus.client import ModbusSerialClient
from socket_tcp import *
from src.commands_parse import execute_command
import share_variables as sv
from remote_control_IO import io_relay_controller
from remote_control_alarm import ModbusAlarm
from remote_detect_current import current_detector
from exception_logger import *
from datetime import datetime


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

    while True:
        with (lock):
            result = execute_command("read", devices)
            #print(sv.RS485_devices_reading)
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
    none_reading_timeslot = datetime.now()
    while True:
        with lock:
            tcp_data = server.read_from_client()
            cur = datetime.now()
            if tcp_data is not None:
                sv.tcp_read_json_information["conveyor_state"] = tcp_data["conveyor"]
                sv.tcp_read_json_information["robot"] = tcp_data["robot"]
                sv.tcp_read_json_information["temperature_sensors"] = tcp_data["temperature"]
                sv.ui_commands["start_signal"] = tcp_data["start"]
                sv.ui_commands["pause_signal"] = tcp_data["pause"]
                sv.ui_commands["shutdown_signal"] = tcp_data["stop"]
                none_reading_timeslot = cur
            sv.tcp_update_period = (cur - none_reading_timeslot).total_seconds()

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
            sv.state_variable["port_connection_flag"] = True
            devices_config = configs["devices"]
            for spec in devices_config:
                device_type = spec.pop('type')
                if device_type == 'alarm' and spec["connection"]:
                    devices[spec["name"]] = (ModbusAlarm(serial_client=serial_client,
                                                         name=spec["name"], unit=spec["unit"]))
                elif device_type == 'relays' and spec["connection"]:
                    devices[spec["name"]] = (io_relay_controller(serial_client=serial_client,
                                                                 name=spec["name"], unit=spec["unit"],
                                                                 small_port=spec["small_port"]))
                elif device_type == 'current_sensor' and spec["connection"]:
                    devices[spec["name"]] = (current_detector(serial_client=serial_client,
                                                              name=spec["name"], unit=spec["unit"]))
            '''
            init a dict to maintain device read data, continuously failure read times and connection flag
            check device connection, check 10 times to do connection with all devices
            '''
            devices_read = configs["devices_read"]
            for device in devices_read:
                if device in devices.keys():
                    sv.RS485_devices_reading[device] = None
                    sv.read_failure_times[device] = 0
            for device in devices:
                sv.devices_connection_flag[device] = False
            execute_command("check", devices)
        else:
            sv.state_variable["port_connection_flag"] = False
            print("port_connection problem")
    return devices


def socket_tcp_init():
    """
    Based on the socket_config.yaml to create a tcp connection
    :return: successful connection return socket instance, otherwise None
    """
    socket_server = None
    config_path = '../config/socket_config.yaml'
    configs = None
    try:
        configs = load_configuration(config_path)
        configs = configs["tcp"][0]
    except Exception as e:
        sv.state_variable["socket_connection_flag"] = False
        print(e)
        return None
    try:
        if configs["connection"]:
            socket_server = tcp_server(host=configs["host"], port=configs["port"],
                                       time_out=configs["connection_time_out"])
            sv.state_variable["socket_connection_flag"] = socket_server.connect_client(
                waiting_time_out=configs["waiting_time_out"])
        else:
            sv.state_variable["socket_connection_flag"] = True
    except Exception as e:
        print(e)
        sv.state_variable["socket_connection_flag"] = False
    return socket_server


def control_system_run():
    """
    prepare devices and tcp socket connection. Then launch two thread to update readings from
    devices and tcp socket. Besides, a finite state machine is launched and it read devices' data
    and tcp information to execute with a set of rules
    :return:
    """
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
    print(f"RS485_devices_reading{sv.RS485_devices_reading}")
    print(f"devices_connection_flag{sv.devices_connection_flag}")
    print(f"read_failure_times{sv.read_failure_times}")
    print(f"tcp_information{sv.tcp_read_json_information}")
    print(f"ui_commands{sv.ui_commands}")
    for key,val in sv.state_variable.items():
        print(f"{key}:{val}")
    exception_handler_system = StateMachine(system_start_state(), lock, devices, sleep_time=0.1)
    exception_handler_system.run()
    # for thread in threads:
    #     thread.join()


if __name__ == '__main__':
    control_system_run()
