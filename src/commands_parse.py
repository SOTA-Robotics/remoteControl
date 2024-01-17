from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
import time
from share_variables import current_read_failure_times, io_output_read_failure_times, io_input_read_failure_times


def command_shutdown(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                     current_controller: fengkong_current_detector):
    io_controller.set_all_switches(0)
    result = io_controller.read_outputs(address=0, count=8)
    alarm_controller.stop_alarm()
    return result


def command_start(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                  current_controller: fengkong_current_detector):
    io_controller.set_all_switches(1)
    result = io_controller.read_outputs(address=0, count=8)
    return result


def command_read(io_controller: zhongsheng_io_relay_controller,
                 current_controller: fengkong_current_detector):
    '''
    read the RS485 all result including current,switches' inputs and outputs
    :param io_controller: zhongsheng_io_relay_controller
    :param current_controller: fengkong_current_detector
    :return:
    '''
    global current_read_failure_times
    global io_input_read_failure_times
    global io_output_read_failure_times
    current_result_temp = None
    io_input_temp = []
    io_output_temp = []
    result = current_controller.read_current()
    if result:
        current_read_failure_times = 0
        current_result_temp = result
    else:
        current_read_failure_times += 1

    input_result_1to6 = io_controller.read_input_conditions(address=0, count=0x6);
    if input_result_1to6 is not None:
        temp_7to8 = io_controller.read_input_conditions(address=6, count=0x2)
        if input_result_1to6 and temp_7to8:
            io_input_read_failure_times = 0
            io_input_temp = input_result_1to6 + temp_7to8
        else:
            io_input_read_failure_times += 1
    result = io_controller.read_outputs(address=0, count=8)
    if result:
        io_output_read_failure_times = 0
        io_output_temp = result
    else:
        io_output_read_failure_times += 1
    return current_result_temp, io_input_temp, io_output_temp


def command_error(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                  current_controller: fengkong_current_detector):
    result = command_shutdown(alarm_controller, io_controller, current_controller);
    alarm_controller.play_alarm();


def check_devices_connection(io_controller: zhongsheng_io_relay_controller
                             , current_detector: fengkong_current_detector, modbusalarm: ModbusAlarm):
    '''
    check if all devices are connected including current sensor, switches and the alarm
    :param io_controller:
    :param current_detector:
    :param modbusalarm:
    :return:
    '''
    alarm_connection_flag = False;
    io_connection_flag = False;
    current_connection_flag = False;
    devices_connection_flag = False;
    times = 0;
    while times < 10:
        alarm_connection_flag = modbusalarm.check_connection(addr=1);
        io_connection_flag = io_controller.check_connection(addr=0);
        time.sleep(0.1);
        current_connection_flag = True if current_detector.read_current() else False;
        if not alarm_connection_flag or not io_connection_flag or not current_connection_flag:
            devices_connection_flag = False;
            times += 1;
        else:
            devices_connection_flag = True;
            break;
    return alarm_connection_flag, io_connection_flag, current_connection_flag, devices_connection_flag


command_functions = {
    "shut_down": command_shutdown,
    "start": command_start,
    "read": command_read,
    "check": check_devices_connection
}


def execute_command(command, *args):
    if command in command_functions:
        return command_functions[command](*args)
    else:
        print("invalid command")
