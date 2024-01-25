import share_variables as sv
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


def pause_system(devices):
    """
    stop devices except robot
    :param devices:
    :return:
    """
    if "io_relays1" in devices.keys():
        stop_list = []
        stop_list.append(sv.configurations["io_output_wf_port_num"])
        stop_list.append(sv.configurations["io_output_cvy_num"])
        devices["io_relays"].control_switches(stop_list,[])

def handle_exception(error_list: list, devices: dict):
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    if error_list:
        sv.my_logger.log_json_information(date, tme, error_code=error_list, debug_condition=True)
        if "io_relays1" in devices:
            if "alarm1" in devices:
                print("here")
                devices["alarm1"].play_alarm()
            # for error in error_list:
            #     if error == 0x501:
            #         if sv.state_variable["socket_connection_flag"]:
            #             devices["io_relays1"].set_all_switches(sv.STOP_BIT)
            #         return system_waiting_state()
            #     elif error == 0x402:
            #         devices["io_relays1"].set_all_switches(sv.STOP_BIT)
            #         return system_waiting_state()
            #     elif error == 0x403:
            #         devices["io_relays1"].set_all_switches(sv.STOP_BIT)
            #         return system_waiting_state()
            if any(item in sv.error_stop_list for item in error_list):
                devices["io_relays1"].set_all_switches(sv.STOP_BIT)
                return system_waiting_state()
        return None


def check_exception():
    """
    check if there are any considered exception problems in the system,
    including connection problem, and all subsystems running conditional problems
    and log the failure exception msg to the file defined in package.json
    :return: False for occurrence of problems; True for no problems
    """
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    # latest_logging = sv.my_logger.read_json_information()
    # if latest_logging and not latest_logging["debug_condition"]:
    #     return False
    error_code_list = check_connection()
    if sv.tcp_read_json_information:
        if (sv.tcp_read_json_information["temperature_sensors"] and
                max(sv.tcp_read_json_information["temperature_sensors"]) > sv.configurations["temperature_threshold"]):
            error_code_list.append(0x401)
        if not sv.tcp_read_json_information["robot_state"]:
            error_code_list.append(0x402)
        if not sv.tcp_read_json_information["conveyor_state"]:
            error_code_list.append(0x403)

    if "current_sensor1" in sv.RS485_devices_reading and (sv.RS485_devices_reading["current_sensor1"] is not None
                                                          and sv.RS485_devices_reading["current"] < sv.configurations[
                                                              "current_threshold"]):
        error_code_list.append(0x404)
    if error_code_list:
        hex_strings = [hex(num) for num in error_code_list]
        print(hex_strings)
        # sv.my_logger.log_json_information(date, tme, error_code=error_code_list, debug_condition=True)
        print("Exceptions' problem")
    return error_code_list


def exception_type(error_code_list):
    if error_code_list:
        if all(item in sv.error_stop_list for item in error_code_list):
            return "error"
        if all(item in sv.error_warning_list for item in error_code_list):
            return "warning"
    return "normal"

def check_connection():
    """
    check if all devices are connected including RS485device, Socket device
    and log the failure exception msg to the file defined in package.json
    :return: False for occurrence of connection problems; True for no connection
    problems
    """
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    error_code_list = []
    soft_connection_error = [0x501, 0x502]
    if not sv.state_variable["socket_connection_flag"]:
        error_code_list.append(0x501)
    if not sv.state_variable["port_connection_flag"]:
        error_code_list.append(0x502)
    if sv.state_variable["socket_connection_flag"] and sv.tcp_update_period > 30:
        print(sv.tcp_update_period)
        error_code_list.append(0x503)
    if sv.devices_connection_flag:
        idx = 0
        for key, val in sv.devices_connection_flag.items():
            print(f"{key}:{val}")
            idx += 1
            if val is False:
                error_code_list.append(0x502 + idx)
    if error_code_list:
        print(error_code_list)
        if all(element in error_code_list for element in soft_connection_error):
            for element in soft_connection_error:
                if element in error_code_list:
                    print(f"soft connection problem: {element}")
        # else:
        #     my_logger.log_json_information(date, tme, error_code=error_code_list,
        #                                debug_condition=False)
    return error_code_list


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
        print(sv.RS485_devices_reading["io_relays1"][0][sv.configurations["io_emergency_stop_port_num"]-1])
        print(sv.RS485_devices_reading)
        if "io_relays1" in devices:
            devices["io_relays1"].set_all_switches(sv.STOP_BIT)
        result = check_exception()
        if sv.ui_commands["shutdown_signal"]:
            sv.ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        if exception_type(result) != "error":
            if sv.ui_commands["start_signal"]:
                sv.ui_commands["start_signal"] = False
                # sv.my_logger.debug_finished()
                return system_start_state()
            elif ("io_relays1" in sv.RS485_devices_reading and
                  (sv.RS485_devices_reading["io_relays1"] and
                   sv.RS485_devices_reading["io_relays1"][0][
                       sv.configurations["io_input_es_port_num"]-1] == sv.STOP_BIT)):
                return system_waiting_state()
            elif ("io_relays1" in sv.RS485_devices_reading and
                  sv.RS485_devices_reading["io_relays1"] and
                  sv.RS485_devices_reading["io_relays1"][0][
                      sv.configurations["io_input_es_port_num"]-1] == sv.START_BIT):
                print("waiting return start state")
                return system_start_state()
        else:
            print("waiting_state:error still persist")
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
        state = handle_exception(check_exception(), devices)
        if "io_relays1" in devices and sv.RS485_devices_reading["io_relays1"][0]:
            print(sv.RS485_devices_reading["io_relays1"])
            print(sv.RS485_devices_reading["io_relays1"][0][sv.configurations["io_input_es_port_num"]-1])
        if "alarm1" in devices.keys():
            devices["alarm1"].stop_alarm()
        if state is not None:
            return state
        if sv.ui_commands["shutdown_signal"]:
            sv.ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        elif ("io_relays1" in sv.RS485_devices_reading and
              (sv.RS485_devices_reading["io_relays1"] and
               sv.RS485_devices_reading["io_relays1"][0][
                   sv.configurations["io_input_es_port_num"]-1] == sv.STOP_BIT)):
            print("emergency stop")
            return system_waiting_state()
        else:
            result = self.start_in_sequence(devices)
            if result is not None:
                return result
            return system_start_state(self.state)

    def start_in_sequence(self, devices):
        """
        constraint the system operates on order.
        brief description: The system should be run manually and the control system
                            then in charge of the running of the system, pause the system when necessarily.

        states' transition: there are three states including state_stage_0 and state_stage_1, and state_stage_2

        state_stage_0: waits all physical switches are release(start) and enters state_stage_1
        state_stage_1: detected all physical switches are starts' mode, make all relays start as well
        state_stage_2: any physical switches are pressed then enter waiting_state
        :param devices: devices list
        :return:
        """
        if self.state == "start_stage_0":
            if "io_relays1" in sv.RS485_devices_reading:
                if (sv.RS485_devices_reading["io_relays1"] and len(sv.RS485_devices_reading["io_relays1"][0]) == 8 and
                        sv.configurations["start_list"] == sv.RS485_devices_reading["io_relays1"][0]):
                    self.state = sv.start_state[self.state]
                else:
                    self.state = self.state
            else:
                self.state = sv.start_state[self.state]
        elif self.state == "start_stage_1":
            if "io_relays1" in sv.RS485_devices_reading:
                print("stop devices")
                devices["io_relays1"].set_all_switches(sv.START_BIT)
                result = devices["io_relays1"].read_outputs(address=0, count=8)
            else:
                result = sv.configurations["start_list"]
            if result and len(result) == 8:
                if result == sv.configurations["start_list"]:
                    self.state = sv.start_state[self.state]
        elif self.state == "start_stage_2":
            if "io_relays1" in devices:
                io_input = sv.RS485_devices_reading["io_relays1"][0]
                if io_input:
                    for val in io_input:
                        if val == sv.STOP_BIT:
                            return system_waiting_state()
        return None


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
        if sv.ui_commands["start_signal"]:
            sv.ui_commands["start_signal"] = False
            return system_start_state()

        self.shutdown_in_sequence(devices)
        if self.state == "shutdown_stage_2":
            return system_start_state()
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
        if self.state == "shutdown_stage_0":
            if "io_relays1" in devices:
                result = devices["io_relays"].set_all_switches(sv.STOP_BIT)
                # result = io_controller.read_outputs(address=0,count=8);
                print("stop devices")
                physical_relays = sv.RS485_devices_reading["io_output"]
                if physical_relays and len(physical_relays) != 8:
                    self.state = "shutdown_stage_0"
                else:
                    if physical_relays == sv.configurations["stop_list"]:
                        self.state = sv.shut_down_state[self.state]
                    else:
                        self.state = "shutdown_stage_0"
            else:
                self.state = sv.shut_down_state[self.state]
        elif self.state == "shutdown_stage_1":
            '''
            wait user to shutdown all physical relays
            '''
            if "io_relays1" in devices:
                if (sv.RS485_devices_reading["io_relays1"] and
                        sv.RS485_devices_reading["io_relays1"][0] == sv.configurations["stop_list"]):
                    self.state = sv.shut_down_state[self.state]
                    print("System can be shutdown here")
            else:
                print("System can be shutdown here")
                self.state = sv.shut_down_state[self.state]
        elif self.state == "shutdown_stage_2":
            '''
            shut down the system
            '''
            print("end here")
            # os.system("shutdown now")
