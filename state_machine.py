from exception_logger import *
from datetime import datetime

'''
shared variables between state machine and main_controller
'''

configurations = load_configuration()
my_logger = LoggingSystem(logger_name=configurations["logger_name"],
                          filename=configurations["logging_path"], level=logging.ERROR)
latest_logging = my_logger.read_json_information()

check_exception_logging_flag = True
if latest_logging is not None and latest_logging["mark_condition"]:
    check_exception_logging_flag = True
elif latest_logging is not None and not latest_logging["mark_condition"]:
    check_exception_logging_flag = False
else:
    check_exception_logging_flag = True

io_input = []
io_output = []
current_result = 0

shutdown_signal = False
start_signal = False

state_variable = {
    "socket_connection_flag": False,
    "port_connection_flag": False,
    "io_connection_flag": False,
    "current_connection_flag": False,
    "alarm_connection_flag": False,
    "devices_connection_flag": False,
    "command_codes": "read",
}

tcp_data = {}


class State:
    """
    class state
    """

    def __int__(self, name):
        self.name = name

    def on_event(self):
        pass


class StateMachine:
    def __init__(self, initial_state, lock):
        self.current_state = initial_state
        self.lock = lock

    def run(self):
        while True:
            with self.lock:
                self.current_state = self.current_state.on_event()


def check_physical_swtiches():
    """
    TO BE FINISHED
    :return:
    """
    global io_input
    global io_output

    return True


def check_exception():
    """
    TO BE FINISHED
    :return:
    """

    return True


def check_emergency_stop_switch():
    """
    TO BE FINISHED
    check the main emergency stop switch state
    :return:
    """

    return True


def check_exception_code():
    """
    TO BE FINISHED
    check what exception problem and return as predefined exception code
    :return:
    """

    return 1


class system_normal_waiting_state(State):
    """
    system normal waiting state: system wait to start
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global client_connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output
        global state_variable

        if shutdown_signal:
            return system_shutdown_state()
        elif check_emergency_stop_switch():
            return system_emergency_stop_state()
        elif not check_exception_logging_flag:
            return system_shutdown_state()
        elif client_connection_flag:
            return system_ready_state()
        else:
            return self


class system_ready_state(State):
    """
    system ready
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global socket_connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output

        if shutdown_signal:
            return system_shutdown_state()
        elif not check_exception_logging_flag:
            return system_ready_state()
        elif check_emergency_stop_switch():
            return system_emergency_stop_state()
        else:
            return system_boosting_state()


class system_boosting_state(State):
    """
    system is boosting, run all subsystems
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global io_input
        global io_output
        global state_variable
        if shutdown_signal:
            return system_shutdown_state()
        elif not check_exception_logging_flag:
            return system_ready_state()
        elif check_emergency_stop_switch():
            return system_emergency_stop_state()
        elif check_physical_swtiches():  # check if all physical switches are on to allow it control system
            return system_boosting_state()
        else:
            return system_operation_state()


class system_operation_state(State):
    '''
    system is operating
    '''

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global socket_connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output
        if shutdown_signal:
            return system_shutdown_state()
        elif not check_exception_logging_flag:
            return system_ready_state()
        elif check_emergency_stop_switch():
            return system_emergency_stop_state()
        return system_operation_state()


class system_exception_state(State):
    """
    system has detected exceptions
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global socket_connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output
        # write down how to record the exception and keep checking if the exception is amended or not
        if check_exception():
            '''
            record the exception here and keep checking if the exception is cleared
            '''
            result = check_exception_code()
            current_date_time = datetime.now()
            date = current_date_time.strftime("%Y-%m-%d")
            time = current_date_time.strftime("%H:%M:%S")

            my_logger.log_json_information(date=date, time=time, error_code=result, debug_condition=False)
            if shutdown_signal:
                return system_shutdown_state()
            else:
                '''
                can add conditional operations for different situation 
                such as the system has been cut off power and wait for a specific amount of time then shut down itself
                '''
                return system_exception_state()
        else:
            return system_normal_waiting_state()


class system_shutdown_state(State):
    """
    system is shuting down
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global _connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output
        '''
        system shut down operation here
        '''
        return system_shutdown_state()


class system_emergency_stop_state(State):
    """
    system detect emergency_switch is pushed, all systems are trying to stop
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global client_connection_flag
        global check_exception_logging_flag
        global io_input
        global io_output
        '''
        digital relay are all off and stop all subsystems running
        '''

        return system_shutdown_state()


class system_reset_state(State):
    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global client_connection_flag
        global check_exception_logging_flag
        global io_input
        '''
        reset all the control devices in initial states
        '''

        return system_waiting_state()


class system_waiting_state(State):
    """
    system do nothing and waits commands
    """

    def on_event(self):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal
        global start_signal
        global client_connection_flag
        global check_exception_logging_flag
        global io_input
        if start_signal:
            return system_normal_waiting_state()
        elif shutdown_signal:
            return system_shutdown_state()
