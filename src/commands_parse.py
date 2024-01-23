def command_shutdown(devices):
    """
    shutdown all output relays
    :param devices: a list of devices
    :return: list of the output relays' conditions
    """
    if "io_relays1" in devices.keys():
        devices["io_relays1"].set_all_switches(0)
        result = devices["io_relays1"].read_outputs(address=0, count=8)
        if "alarm1" in devices:
            devices["alarm1"].stop_alarm()
    return result


def command_start(devices):
    """
    start all output relays
    :param devices: a list of devices
    :return: list of the output relays' conditions
    """
    if "io_relays1" in devices.keys():
        devices["io_relays1"].set_all_switches(1)
        result = devices["io_relays1"].read_outputs(address=0, count=8)
        if "alarm1" in devices:
            devices["alarm1"].stop_alarm()
    return result


def command_read(devices):
    """
    read the RS485 all result including current,switches' inputs and outputs
    :param devices: a list of devices
    :return:
    """
    global read_failure_times
    global RS485_devices_reading

    for key in RS485_devices_reading:
        if key in devices:
            RS485_devices_reading[key] = devices[key].read()
            if isinstance(RS485_devices_reading[key],int):
                read_failure_times[key] = 0
            elif isinstance(RS485_devices_reading[key],list):
                read_failure_times[key] = 0
            else:
                read_failure_times[key] += 1


def command_error(devices):
    """
    control io_relays to stop whole system as well as let alarm play
    :param devices: a list of devices
    :return:
    """
    result = command_shutdown(devices)
    if "alarm1" in devices:
        devices["alarm1"].play_alarm()


def check_devices_connection(devices):
    """
    check if all devices are connected including current sensor, switches and the alarm
    try 5 times if devices are connected
    :param devices: a list of devices
    :return:
    """
    global devices_connection_flag
    flags = []
    times = 0
    while times < 5:
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
