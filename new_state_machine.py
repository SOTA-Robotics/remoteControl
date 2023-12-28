

from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
from share_variables import *
from datetime import datetime
import time


class State:
    """
    Father class
    """
    def __int__(self, name,state):
        self.name = name
        self.state = state

    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        pass;

class StateMachine:
    """
    Class for managing finite state machine
    """
    def __init__(self,initial_state:State,lock,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector,sleep_time):
        self.current_state = initial_state
        self.lock = lock
        self.current_controller = current_controller
        self.alarm_controller = alarm_controller
        self.io_controller = io_controller
        self.sleep_time = sleep_time

    def run(self):
        while True:
            with self.lock:
                print(self.current_state.__class__.__name__ + " : " + str(self.current_state.state))
                self.current_state = self.current_state.on_event(self.alarm_controller,
                                                                 self.io_controller,self.current_controller)
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
    state_variable["check_exception_logging_flag"] = not latest_logging["debug_condition"]
    if state_variable["check_exception_logging_flag"]:
        print("The old exception problem still persist")
        return False
    if not check_connection():
        print("Connections' problem")
        return False

    # log_info = my_logger.read_json_information();
    # if log_info is not None and not log_info["debug_condition"]:
    #     return False;
    if tcp_read_json_information:
        if (tcp_read_json_information["temperature_sensors"] and
                max(tcp_read_json_information["temperature_sensors"]) > configurations["temperature_threshold"]):
            error_code_list.append(0x06)
        if not tcp_read_json_information["robot_state"]:
            error_code_list.append(0x07)
        if not tcp_read_json_information["conveyor_state"]:
            error_code_list.append(0x08)
    if RS485_devices_reading["current"] is not None and RS485_devices_reading["current"] < configurations["current_threshold"]:
        error_code_list.append(0x09)
    if not error_code_list:
        my_logger.log_json_information(date,tme,error_code=error_code_list, debug_condition=False)
        state_variable["check_exception_logging_flag"] = True
        print("other exceptions' problem")
        return False
    return True


def check_connection():
    '''
    check if all devices are connected including RS485device, Socket device
    and log the failure exception msg to the file defined in package.json
    :return: False for occurrence of connection problems; True for no connection
    problems
    '''
    global state_variable
    global my_logger
    global configurations
    cur = datetime.now()
    date = cur.strftime('%Y:%m:%d')
    tme = cur.strftime('%H:%M:%S')
    error_code_list = []
    if not state_variable["socket_connection_flag"]:
        error_code_list.append(0x01)
    if not state_variable["port_connection_flag"]:
        error_code_list.append(0x02)
    if not state_variable["io_connection_flag"]:
        error_code_list.append(0x03)
    if not state_variable["current_connection_flag"]:
        error_code_list.append(0x04)
    if not state_variable["alarm_connection_flag"]:
        error_code_list.append(0x05)
    if error_code_list:
        my_logger.log_json_information(date,tme,error_code=error_code_list,
                                       debug_condition=False)
        state_variable["check_exception_logging_flag"] = True
        return False
    else:
        return True


class system_waiting_state(State):
    """
    system normal waiting state: system wait to start
    In this state's situations: exception occurs;the emergency button is switched on
    Out of this state's situations: the emergency button is released; start command;
                                    shutdown command.
    otherwise: system will remain this state
    """
    def __init__(self,state = None):
        self.state = state
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        global ui_commands
        global RS485_devices_reading
        global configurations
        #print("io input status: " + str(RS485_devices_reading["io_input"]))
        io_controller.set_all_switches(STOP_BIT)
        result = io_controller.read_outputs(address=0, count=8)
        if ui_commands["shutdown_signal"]:
            ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        elif ui_commands["start_signal"]:
            ui_commands["start_signal"] = False
            my_logger.debug_finished()
            return system_start_state()
        elif not check_exception():
            if RS485_devices_reading["current"] < configurations["current_threshold"]:
                return system_shutdown_state()
            return system_waiting_state()
        elif (RS485_devices_reading["io_input"] and
              RS485_devices_reading["io_input"][configurations["io_emergency_stop_port_num"]] == STOP_BIT):
            return system_waiting_state()
        elif (RS485_devices_reading["io_input"] and
              RS485_devices_reading["io_input"][configurations["io_emergency_stop_port_num"]] == START_BIT):
            return system_start_state()
        else:
            return system_waiting_state()


class system_start_state(State):
    """
    The system allow to be run
    IN this state's situations: all connection and exception problems are cleaned
    Out of this state's situations: shutdown command; exception occur
    """
    def __init__(self,state = "state_stage_0"):
        self.state = state

    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        global RS485_devices_reading
        global ui_commands
        if ui_commands["shutdown_signal"]:
            ui_commands["shutdown_signal"] = False
            return system_shutdown_state()
        elif not check_exception():
            return system_waiting_state()
        elif (RS485_devices_reading["io_input"] and
              RS485_devices_reading["io_input"][configurations["io_emergency_stop_port_num"]] == STOP_BIT):
            return system_waiting_state()
        else:
            self.start_in_sequence(io_controller)
            return system_start_state(self.state)

    def start_in_sequence(self,io_controller: zhongsheng_io_relay_controller):
        '''
        constraint the system operates on order.
        brief description: The system should be run manually and the control system
         then in charge of the running of the system, pause the system when necessarily.
        :param io_controller: io_controller
        :return:
        '''
        global RS485_devices_reading
        global start_state
        global configurations
        #print("io input status: "+str(RS485_devices_reading["io_input"]))
        if self.state == "state_stage_0":
            if RS485_devices_reading["io_input"] and len(RS485_devices_reading["io_input"]) == 8:
                start_list = [START_BIT]*7
                if(start_list == RS485_devices_reading["io_input"][:7]):
                    self.state = start_state[self.state]
        elif self.state == "state_stage_1":
            result = io_controller.set_all_switches(START_BIT);
            result = io_controller.read_outputs(address=0,count=8)
            if result and len(result) == 8:
                start_list = [START_BIT]*8
                if result == start_list:
                    self.state = start_state[self.state]
        elif self.state == "state_stage_2":
            io_input = RS485_devices_reading["io_input"]
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
    def __init__(self,state = "shutdown_stage_0"):
        self.state = state

    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        #print(f"The class name is:{self.__class__.__name__}")
        if ui_commands["start_signal"]:
            ui_commands["start_signal"] = False
            return system_start_state()

        self.shutdown_in_sequence(io_controller)
        return system_shutdown_state(self.state)


    def shutdown_in_sequence(self,io_controller: zhongsheng_io_relay_controller):
        """
        To ensure the system be shutdown correctly and safely operate next time
        wait until all physical relays or switches are turned off. Then control
        system release the relays and commands itself and cv system power off
        :param io_controller: io_controller object
        :return:
        """
        global RS485_devices_reading
        global shut_down_state
        if self.state == "shutdown_stage_0":
            result = io_controller.set_all_switches(STOP_BIT)
            # result = io_controller.read_outputs(address=0,count=8);
            physical_relays = RS485_devices_reading["io_output"]
            if physical_relays and len(physical_relays) != 8:
                self.state = "shutdown_stage_0"
            else:
                stop_list = [STOP_BIT]*8
                if physical_relays == stop_list:
                    self.state = shut_down_state[self.state]
                else:
                    self.state = "shutdown_stage_0"
        elif self.state == "shutdown_stage_1":
            '''
            wait user to shutdown all physical relays
            '''
            io_input = RS485_devices_reading["io_input"]
            stop_list = [STOP_BIT]*1
            if io_input and io_input[:1] == stop_list:
                self.state = shut_down_state[self.state]
                print("System can be shutdown here")

        elif self.state == "shutdown_stage_2":
            result = io_controller.set_all_switches(START_BIT)
            # result = io_controller.read_outputs(address=0, count=8);
            output_relays = RS485_devices_reading["io_output"]
            start_list = [START_BIT] * 8
            if output_relays and len(output_relays) == 8:
                if output_relays == start_list:
                    print("system should be shutdown here")
                    #os.system("shutdown now")


