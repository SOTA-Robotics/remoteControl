from remote_control_alarm import ModbusAlarm
from remote_control_IO import io_relay_controller
from remote_detect_current import current_detector
import time
from share_variables import current_read_failure_times, io_output_read_failure_times, io_input_read_failure_times


def command_shutdown(alarm_controller: ModbusAlarm, io_controller: io_relay_controller,
                     current_controller: current_detector):
    io_controller.set_all_switches(0)
    result = io_controller.read_outputs(address=0, count=8)
    alarm_controller.stop_alarm()
    return result


def command_start(alarm_controller: ModbusAlarm, io_controller: io_relay_controller,
                  current_controller: current_detector):
    io_controller.set_all_switches(1)
    result = io_controller.read_outputs(address=0, count=8)
    return result


def command_read(devices):
    '''
    read the RS485 all result including current,switches' inputs and outputs
    :param devices:
    :return:
    '''
    global read_failure_times
    global RS485_devices_reading

    for key in RS485_devices_reading:
        if key in devices:
            RS485_devices_reading[key] = devices[key].read()
            if isinstance(RS485_devices_reading[key],int) and RS485_devices_reading[key] is None:
                read_failure_times[key] += 1
            elif isinstance(RS485_devices_reading[key],list) and None in RS485_devices_reading[key]:
                read_failure_times[key] += 1
            else:
                read_failure_times[key] = 0


def command_error(alarm_controller: ModbusAlarm, io_controller:io_relay_controller,
                  current_controller: current_detector):
    result = command_shutdown(alarm_controller, io_controller, current_controller)
    alarm_controller.play_alarm()


def check_devices_connection(devices):
    '''
    check if all devices are connected including current sensor, switches and the alarm
    :param devices:
    :return:
    '''
    global devices_connection_flag
    flags = []
    times = 0
    while times < 10:
        for key, device in devices.items():
            devices_connection_flag[key] = True if device.check() else False
        if any(item is False for item in devices_connection_flag.values()):
            times += 1
        else:
            break


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
