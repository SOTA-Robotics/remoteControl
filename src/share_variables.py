"""
shared variables between state machine and main_controller
"""
from src.exception_logger import *
'''
initialize the logger and read the logging msg of the last line
'''
configurations = load_configuration("../../config/package.yaml")
if configurations is None:
    raise Exception("configuration loading error")
my_logger = LoggingSystem(logger_name=configurations["logger_name"],
                          filename=configurations["logging_path"], level=logging.ERROR)
latest_logging = my_logger.read_json_information()

check_exception_logging_flag = False
if latest_logging is not None and not latest_logging["debug_condition"]:
    check_exception_logging_flag = True

'''
share variable regions
state_variable: flags for recording if the connections are success or not
                False for failure and True for success
                             
ui_commands: start,shutdown and pause signal are conveyed from outside
'''
state_variable = {"socket_connection_flag": False, "port_connection_flag": False}

'''
RS485_devices_reading: stores devices reading data from RS485
'''
RS485_devices_reading = {}

'''
variables to record the times of failure of trying read 485 devices
'''
current_read_failure_times = 0
io_input_read_failure_times = 0
io_output_read_failure_times = 0
read_failure_times ={}
devices_connection_flag = {}

ui_commands = {
    "shutdown_signal": False,
    "start_signal": False,
    "pause_signal": False
}

'''
tcp read json format information,
Format is:
        {conveyor_state:bool,
        robot_state:bool,
        temperature_sensors = [sensor1_value,sensor2_value,sensor3_value,sensor4_value],
        }
'''
tcp_read_json_information ={
    "conveyor_state": True,
    "robot_state": True,
    "temperature_sensors": [0, 0, 0, 0],
}

'''
ministates for finite state machine
'''
shut_down_state = {
    '''
    shutdown mini states:
                    shutdown_stage_1:
                    shutdown_stage_2:
    '''
    "shutdown_stage_0":"shutdown_stage_1",
    "shutdown_stage_1": "shutdown_stage_2",
}
start_state = {
    '''
    start mini states:
                    start_stage_1:
                    start_stage_2:
    '''
    "start_stage_0": "start_stage_1",
    "start_stage_1": "start_stage_2"
}

'''
simply define bit's value for STOP and START
'''
STOP_BIT = 1
START_BIT = 0


'''
list to represent start or stop for physical switches
'''
start_list = configurations["start_bits"]
stop_list = configurations["stop_bits"]

'''
dict to store different devices
'''
device_managers = {}

