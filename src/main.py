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


def io_controller_handler(io_controller: zhongsheng_io_relay_controller
                          , current_detector: fengkong_current_detector, timeout, lock):
    """
    Threading function to read io input and output as well as current.
    This function run a specific amount of time periodically
    :param io_controller: zhongsheng_io_relay_controller object
    :param current_detector: fengkong_current_detector object
    :param timeout: the period of time between wake and sleep for this threading
    :param lock: lock for shared data structure between socket and threading
    :return:
    """

    print("io_controller_handler start")
    global RS485_devices_reading

    while True:
        with (lock):
            result = execute_command("read", io_controller, current_detector)
            RS485_devices_reading["io_input"] = result[1]
            RS485_devices_reading["io_output"] = result[2]
            RS485_devices_reading["current"] = result[0]
        time.sleep(timeout)


def tcp_handler(server: tcp_server, timeout, lock):
    '''
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
    '''
    global tcp_data
    global RS485_devices_reading
    global ui_commands
    global tcp_read_json_information
    while True:
        with lock:
            tcp_data = server.read_from_client()
            if (tcp_data != None):
                print(tcp_data)
                tcp_read_json_information["conveyor_state"] = tcp_data["conveyor"]
                tcp_read_json_information["robot"] = tcp_data["robot"]
                tcp_read_json_information["temperature_sensors"] = tcp_data["temperature"]
                ui_commands["start_signal"] = tcp_data["start"]
                ui_commands["pause_signal"] = tcp_data["pause"]
                ui_commands["shutdown_signal"] = tcp_data["stop"]

                # print(RS485_devices_reading)
        time.sleep(timeout)


def cv_status_monitor_handler(server: tcp_server, timeout, lock):
    '''
    check rs485 devices as well as cv system
    :param server:
    :param timeout:
    :param lock:
    :return:
    '''
    while True:
        with lock:
            temp = 1
        time.sleep(timeout)


if __name__ == '__main__':
    global state_variable
    threads = []
    lock = threading.Lock()  # lock for shared data structure between socket and threading
    serial_client = ModbusSerialClient(
        method='rtu',
        Framer=Framer.RTU,
        port="/dev/ttyUSB0",
        baudrate=19200,
        parity='N',
        bytesize=8,
        stopbits=1,
        timeout=0.1,
        errorcheck="crc"
    )
    connection = serial_client.connect()
    if connection:
        state_variable["port_connection_flag"] = True
    '''
    initialize three devices
    '''
    modbusalarm = ModbusAlarm(serial_client, unit=1)
    io_relay = zhongsheng_io_relay_controller(serial_client, unit=2, small_port=False)
    current_detector = fengkong_current_detector(serial_client, unit=3)

    '''
    check device connection, check 10 times to do connection with all devices
    '''
    result = execute_command("check", io_relay, current_detector, modbusalarm)
    state_variable["alarm_connection_flag"] = result[0]
    state_variable["io_connection_flag"] = result[1]
    state_variable["current_connection_flag"] = result[2]
    state_variable["devices_connection_flag"] = result[3]

    print(state_variable["alarm_connection_flag"], state_variable["io_connection_flag"],
          state_variable["current_connection_flag"])
    '''
    wait client make tcp connection in specific amount of time 
    '''
    try:
        socket_server = tcp_server(host=configurations["host"], port=configurations["port"],
                                   time_out=configurations["connection_time_out"])
        state_variable["socket_connection_flag"] = socket_server.connect_client(
            waiting_time_out=configurations["waiting_time_out"])
        thread = threading.Thread(target=tcp_handler, args=(socket_server, 0.1, lock))
        thread.start()
        threads.append(thread)
    except Exception as e:
        state_variable["socket_connection_flag"] = True

    '''
    Ready to run exception monitor system and read io and tcp devices 
    '''

    thread = threading.Thread(target=io_controller_handler, args=(io_relay, current_detector, 0.1, lock))
    thread.start()
    threads.append(thread)

    exception_handler_system = StateMachine(system_start_state(), lock,
                                            modbusalarm, io_relay, current_detector,
                                            1)
    exception_handler_system.run()
    for thread in threads:
        thread.join()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
