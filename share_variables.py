"""
shared variables between state machine and main_controller
"""
from exception_logger import *
'''
initialize the logger and read the logging msg of the last line
'''
configurations = load_configuration()
my_logger = LoggingSystem(logger_name=configurations["logger_name"],
                          filename=configurations["logging_path"], level=logging.ERROR)
latest_logging = my_logger.read_json_information()

check_exception_logging_flag = False
if latest_logging is not None and not latest_logging["debug_condition"]:
    check_exception_logging_flag = True

'''
share variable regions
state_variable: flags for recording if the connections are success or not
                False for success and True for failure
                
RS485_devices_reading: stores three variables to manage devices data
                        io_input list, io_output list and current value
                        
ui_commands: start,shutdown and pause signal are conveyed from outside
'''
state_variable = {"socket_connection_flag": False, "port_connection_flag": False, "io_connection_flag": False,
                  "current_connection_flag": False, "alarm_connection_flag": False, "devices_connection_flag": False,
                  "check_exception_logging_flag": check_exception_logging_flag, "command_codes": "read"}

RS485_devices_reading = {
    "io_input": [],
    "io_output": [],
    "current": None
}

'''
variables to record the times of failure of trying read 485 devices
'''
current_read_failure_times = 0
io_input_read_failure_times = 0
io_output_read_failure_times = 0

ui_commands = {
    "shutdown_signal" :False,
    "start_signal" :False,
    "pause_signal" : False
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
    "conveyor_state":False,
    "robot_state":False,
    "temperature_sensors" : [],
}

'''
ministates for finite state machine
'''
shut_down_state = {
    "shutdown_stage_0":"shutdown_stage_1",
    "shutdown_stage_1": "shutdown_stage_2",
}
start_state = {
    "state_stage_0":"state_stage_1",
    "state_stage_1":"state_stage_2"
}

'''
simply define bit's value for STOP and START
'''
STOP_BIT = 1
START_BIT = 0

