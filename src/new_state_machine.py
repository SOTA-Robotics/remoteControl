from share_variables import *
from datetime import datetime
import time
import os


class State:
    """
    Father class
    """

    def __int__(self, name, state):
        self.name = name
        self.state = state

    def on_event(self, device):
        pass;


class StateMachine:
    """
    Class for managing finite state machine
    """

    def __init__(self, initial_state: State, lock, devices, sleep_time):
        self.current_state = initial_state
        self.lock = lock
        self.devices = devices
        self.sleep_time = sleep_time

    def run(self):
        while True:
            with self.lock:
                print(self.current_state.__class__.__name__ + " : " + str(self.current_state.state))
                self.current_state = self.current_state.on_event(self.devices)
            time.sleep(self.sleep_time)


def check_exception():
    '''
    check if there are any considered exception problems in the system,
    including connection problem, and all subsystems running conditional problems
    and log the failure exception msg to the file defined in package.json
    :return: False for occurrence of problems; True for no problems
    '''
    global RS485_devices_reading
    global my_logger
    global configurations
    global state_variable
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    error_code_list = []
    latest_logging = my_logger.read_json_information()
    if latest_logging and not latest_logging["debug_condition"]:
        return False
    if not check_connection():
        print("Connections' problem")
        return False
    if tcp_read_json_information:
        if (tcp_read_json_information["temperature_sensors"] and
                max(tcp_read_json_information["temperature_sensors"]) > configurations["temperature_threshold"]):
            error_code_list.append(0x401)
        if not tcp_read_json_information["robot_state"]:
            error_code_list.append(0x402)
        if not tcp_read_json_information["conveyor_state"]:
            error_code_list.append(0x403)

    if "current_sensor1" in RS485_devices_reading and (RS485_devices_reading["current_sensor1"] is not None
                                                       and RS485_devices_reading["current"] < configurations[
                                                           "current_threshold"]):
        error_code_list.append(0x404)
    if error_code_list:
        my_logger.log_json_information(date, tme, error_code=error_code_list, debug_condition=False)
        print("other exceptions' problem")
        return False
    return True


def check_connection():
    """
    check if all devices are connected including RS485device, Socket device
    and log the failure exception msg to the file defined in package.json
    :return: False for occurrence of connection problems; True for no connection
    problems
    """
    global state_variable
    global my_logger
    global configurations
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    error_code_list = []
    soft_connection_error = [0x501,0x502]
    if not state_variable["socket_connection_flag"]:
        error_code_list.append(0x501)
    if not state_variable["port_connection_flag"]:
        error_code_list.append(0x502)
    if devices_connection_flag:
        idx = 0
        for val in devices_connection_flag.values():
            idx += 1
            if val is False:
                error_code_list.append(0x502 + idx)
    if error_code_list:
        if all(element in error_code_list for element in soft_connection_error):
            for element in soft_connection_error:
                if element in error_code_list:
                    print(f"soft connection problem: {element}")
    else:
        my_logger.log_json_information(date, tme, error_code=error_code_list,
                                       debug_condition=False)
        return False
    return True


class system_waiting_state(State):
    """
    system normal waiting state: system wait to start
    In this state's situations: exception occurs;the emergency button is switched on
    Out of this state's situations: the emergency button is released; start command;
                                    shutdown command.
    otherwise: system will remain this state
    """

    def __init__(self, state=None):
        self.state = state

    def on_event(self, devices):
        global ui_commands
        global RS485_devices_reading
        global configurations
        if "io_relays1" in devices:
            devices["io_relays1"].set_all_switches(STOP_BIT)
            result = devices["io_relays1"].read_outputs(address=0, count=8)
        if ui_commands["shutdown_signal"]:
            ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        elif ui_commands["start_signal"]:
            ui_commands["start_signal"] = False
            my_logger.debug_finished()
            return system_start_state()
        elif not check_exception():
            if ("current_sensor1" in RS485_devices_reading and
                    RS485_devices_reading["current_sensor1"] < configurations["current_threshold"]):
                return system_shutdown_state()
            return system_waiting_state()
        elif ("io_relays" in RS485_devices_reading and
              (RS485_devices_reading["io_relays"] and
               RS485_devices_reading["io_relays"][0][configurations["io_emergency_stop_port_num"]] == STOP_BIT)):
            return system_waiting_state()
        elif ("io_relays" in RS485_devices_reading and
              RS485_devices_reading["io_relays"] and
              RS485_devices_reading["io_relays"][0][configurations["io_emergency_stop_port_num"]] == START_BIT):
            return system_start_state()
        else:
            return system_waiting_state()


class system_start_state(State):
    """
    The system allow to be run
    IN this state's situations: all connection and exception problems are cleaned
    Out of this state's situations: shutdown command; exception occur
    """

    def __init__(self, state="start_stage_0"):
        self.state = state

    def on_event(self, devices):
        global RS485_devices_reading
        global ui_commands
        if ui_commands["shutdown_signal"]:
            ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        elif not check_exception():
            return system_waiting_state()
        elif ("io_relays" in RS485_devices_reading and
              (RS485_devices_reading["io_relays"] and
               RS485_devices_reading["io_relays"][0][configurations["io_emergency_stop_port_num"]] == STOP_BIT)):
            return system_waiting_state()
        else:
            self.start_in_sequence(devices)
            return system_start_state(self.state)

    def start_in_sequence(self, devices):
        '''
        constraint the system operates on order.
        brief description: The system should be run manually and the control system
                            then in charge of the running of the system, pause the system when necessarily.

        states' transition: there are three states including state_stage_0 and state_stage_1, and state_stage_2

        state_stage_0: waits all physical switches are release(start) and enters state_stage_1
        state_stage_1: detected all physical switches are starts' mode, make all relays start as well
        state_stage_2: any physical switches are pressed then enter waiting_state
        :param devices: devices list
        :return:
        '''
        global RS485_devices_reading
        global start_state
        global configurations
        if self.state == "start_stage_0":
            if "io_relays" in RS485_devices_reading:
                if (RS485_devices_reading["io_relays"] and len(RS485_devices_reading["io_relays"][0]) == 8 and
                        configurations["start_list"] == RS485_devices_reading["io_relays"][0]):
                    self.state = start_state[self.state]
                else:
                    self.state = self.state
            else:
                print(start_state)
                self.state = start_state[self.state]
        elif self.state == "start_stage_1":
            if "io_relays" in RS485_devices_reading:
                devices["io_relays"].set_all_switches(START_BIT)
                result = devices["io_relays"].read_outputs(address=0, count=8)
            else:
                result = configurations["start_list"]
            if result and len(result) == 8:
                if result == configurations["start_list"]:
                    self.state = start_state[self.state]
        elif self.state == "start_stage_2":
            if "io_relays" in devices:
                io_input = RS485_devices_reading["io_relays"]
                if io_input:
                    for val in io_input:
                        if val == STOP_BIT:
                            return system_waiting_state()


class system_shutdown_state(State):
    """
    system shutdown mode: control system pause the whole system
                        and wait users shutdown system correctly. Then control system
                        will command control system and cv system shutdown safely


    :param State: None, the state machine determine which state will be passed to
    """

    def __init__(self, state="shutdown_stage_0"):
        self.state = state

    def on_event(self, devices):
        if ui_commands["start_signal"]:
            ui_commands["start_signal"] = False
            return system_start_state()

        self.shutdown_in_sequence(devices)
        return system_shutdown_state(self.state)

    def shutdown_in_sequence(self, devices):
        """
        To ensure the system be shutdown correctly and safely operate next time
        wait until all physical relays or switches are turned off. Then control
        system release the relays and commands itself and cv system power off

        states' transition:
        :param devices: io_controller object
        :return:
        """
        global RS485_devices_reading
        global shut_down_state
        global configurations
        if self.state == "shutdown_stage_0":
            if "io_relays" in devices:
                result = devices["io_relays"].set_all_switches(STOP_BIT)
                # result = io_controller.read_outputs(address=0,count=8);
                physical_relays = RS485_devices_reading["io_output"]
                if physical_relays and len(physical_relays) != 8:
                    self.state = "shutdown_stage_0"
                else:
                    if physical_relays == configurations["stop_list"]:
                        self.state = shut_down_state[self.state]
                    else:
                        self.state = "shutdown_stage_0"
            else:
                self.state = shut_down_state[self.state]
        elif self.state == "shutdown_stage_1":
            '''
            wait user to shutdown all physical relays
            '''
            if "io_relays" in devices:
                if (RS485_devices_reading["io_relays"] and
                        RS485_devices_reading["io_relays"][0] == configurations["stop_list"]):
                    self.state = shut_down_state[self.state]
                    print("System can be shutdown here")
            else:
                print("System can be shutdown here")
                self.state = shut_down_state[self.state]
        elif self.state == "shutdown_stage_2":
            '''
            shut down the system
            '''
            os.system("shutdown now")
