"""
test alarm region
"""
# alarm = Alarm(serial_port="/dev/ttyUSB0", baud_rate= 9600,unit = 0x01);
# alarm.setAlarmVolume(volume=5)
# alarm.playAlarm();
# time.sleep(1);
# alarm.stopAlarm();
# exit(0);


"""
test IO_relay region 
"""
# IO_relay = zhongsheng_IO_relay_controller(serial_port="/dev/ttyUSB0", baud_rate= 38400,unit = 1,timeout=0.1);
# result = IO_relay.read_input_conditions(address= 0x0000,count = 1);
# print(result);
# result = IO_relay.read_single_coil(address= 0x0000);
# print(result);
# time.sleep(1);
# result = IO_relay.switch_single_ouput(address=0x0000, value=True);
# print(result);
# time.sleep(1);
# result = IO_relay.switch_single_ouput(address=0x0000, value=False);

'''
    cant work for 4 output IO_Relay device; maybe work for higher number of output 
'''
# open_switch_list = [1];
# close_switch_list = [];
# result = IO_relay.control_switches(open_switch_list=open_switch_list,close_switch_list=close_switch_list);
# print(result);
# open_switch_list = [];
# close_switch_list = [1];
# result = IO_relay.control_switches(open_switch_list=open_switch_list, close_switch_list=close_switch_list);
# print(result);

'''
test fengkong current detector
'''

"""
Communicate with all devices connected to main bus in rs485
alarm: baud_rate = 9600, id = 1
zhongsheng_IO_Relay: baud_rate = 19200, id = 2
fengkong_current_detector: baud_rate = 19200, id = 3
"""

'''
test loggingSystem class
'''

# my_logger = LoggingSystem(logger_name="error_logger", filename="logging.log");
# cur = datetime.now();
# date = cur.strftime("%Y:%m:%d");
# time = cur.strftime("%H:%M:%S");
# my_logger.log_json_information(date=date, time=time, error_code=1, debug_condition=False, mark_condition=False);
# result = my_logger.read_json_information();
# print(result)
# my_logger.debug_finished();
# result = my_logger.read_json_information();
# print(result)
# my_logger.mark_finish();
# result = my_logger.read_json_information();
# print(result)