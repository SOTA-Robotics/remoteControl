# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pymodbus.client import ModbusSerialClient

from RS485 import *

# class Alarm():
#     def __init__(self,serial_port = "/dev/ttyUSB0",baud_rate = 19200 ,unit = 0x01):
#         '''
#         This is abandoned class due to its non-standard communication protocol
#         compared with modbus RS485
#         :param serial_port: string, default port is /dev/ttyUSB0
#         :param baud_rate: default baud rate, default 19200
#         :param unit: default slave id is 0x01
#         '''
#         self.unit = unit;
#         self.serial = serial.Serial(serial_port, baud_rate)
#         self.SOF = " EF AA ";
#         self.EOF = " EF 55 ";
#     def setAlarmVolume(self,volume = 15):
#         try:
#             ttl_data = "AA 13 01 " + self.to_2bytes(volume);
#             crc = self.own_crc(ttl_data);
#             command = self.SOF + ttl_data + crc + self.EOF;
#             self.write_bytes(command);
#         except Exception as e:
#             print("Wrong to set the alarm volume",e);
#             # this is a try
#
#     def alarmPlayMode(self,mode = 1):
#         '''
#
#         :param mode: set alarm play mode ,default value is 1
#         :return:
#         '''
#         try:
#             ttl_data = "AA 18 01 " + self.to_2bytes(mode) + ' C6';
#             crc = "";
#             command = self.SOF + ttl_data + crc + self.EOF;
#             self.write_bytes(command);
#
#         except Exception as e:
#             print("Wrong to set the alarm play mode",e)
#
#     def setAlarmAddress(self,unit):
#         '''
#
#         :param unit: set alarm slave id
#         :return:
#         '''
#         try:
#             old_id = self.to_2bytes(self.unit);
#             new_id = self.to_2bytes(unit);
#             command = " EF FF "+ old_id + " A2 " + new_id + " EF 55"
#             self.write_bytes(command);
#             self.unit = unit;
#         except:
#             print("Wrong to assign uint ID to alarm device");
#
#     def setAlarmBaudRate(self,baud_rate_choice):
#         '''
#
#         :param baud_rate_choice:integer from 0 to 7, choose baud_rate with table as {0:,1:,2:,3:,4:,5:,6:,7:}
#         :return:
#         '''
#         try:
#             if 7 >= baud_rate_choice >= 0:
#                 old_id = self.to_2bytes(self.unit);
#                 new_baud_rate = self.to_2bytes(baud_rate_choice);
#                 command = " EF FF "+ old_id + " A1 " + new_baud_rate + " EF 55"
#                 self.write_bytes(command);
#             else:
#                 print("Failure to set baud rate, the baud rate choice should be integer between 0 and 7");
#         except Exception as e:
#             print("Wrong to assign new baud rate to alarm device",e);
#
#     def playAlarm(self):
#         '''
#         start to play alarm
#         :return:
#         '''
#         try:
#             id = self.to_2bytes(self.unit);
#             command = self.SOF + id  +"AA 02 00 AC" +  self.EOF;
#             self.write_bytes(command);
#             print('start to play alarm');
#         except Exception as e:
#             print("Failure to let alarm play",e);
#
#     def stopAlarm(self):
#         '''
#         stop to play alarm
#         :return:
#         '''
#         try:
#             id = self.to_2bytes(self.unit);
#             command = self.SOF + id + "AA 03 00 AD" + self.EOF;
#             self.write_bytes(command);
#             print('start to play alarm');
#         except Exception as e:
#             print("Failure to let alarm stop",e);
#
#     def check_configuration(self):
#         '''
#         check alarm configuration, the decode information based on manual files
#         :return:
#         '''
#         # check the configuration
#         self.serial.reset_input_buffer();
#         self.serial.write_bytes('EF FF FF A6 33 EF 55');
#         result = self.serial.read(10);
#         print(['{:02x}'.format(b) for b in result])
#
#     def reset_alarm(self):
#         # reset the alarm as default setting
#         self.serial.reset_input_buffer();
#         self.write_bytes('EF FF FF A7 33 EF 55');
#         result = self.serial.read(7);
#         print(['{:02x}'.format(b) for b in result])
#
#     def write_bytes(self, hex_bytes):
#         """
#         Write a bytes to the modbus server.
#         self.write_bytes("02 06 00 02 00 01 E9 F9")
#         Args:
#             hex_bytes:
#
#         Returns:
#
#         """
#         byte = bytes.fromhex(hex_bytes)
#         self.serial.write(byte)
#
#     def own_crc(self,ttl_data):
#         byte = bytes.fromhex(ttl_data);
#         return hex(sum(byte))[-2:]
#
#     def to_2bytes(self,num):
#         bytes_string = num.to_bytes(1,'big').hex();
#         if( len(bytes_string) <2) :
#             byte_string = '0' + bytes_string;
#         byte_string = " " + bytes_string + " ";
#         return bytes_string;
# See PyCharm help at https://www.jetbrains.com/help/pycharm/


class ModbusAlarm(RS485):
    def __init__(self, serial_client: ModbusSerialClient, unit=0x01):
        """

        :param serial_client: pymodbus serialclient object
        :param unit: the slave id for this device
        """
        super().__init__(serial_client, unit)
        self.unit = unit
        self.client = serial_client

        print("Connected to Modbus RTU device alarm_controller")

    def play_alarm(self):
        '''
        This alarm starts to play
        :return: None for failure to send commands; Values for success to send commands
        '''
        result = self.client.write_register(address=0x01, value=0, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to write register", result)
            return None
        else:
            return result.registers

    def stop_alarm(self):
        """
        This alarm stop playing
        :return: None for failure to send commands; Values for success to send commands
        """
        result = self.client.write_register(address=0x02, value=0, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to write register", result)
            return None
        else:
            return result.registers

    def set_alarm_volume(self,volume=15):
        """
        set alarm volume
        :param volume: uint, volume for this alarm
        :return: None for failure to send commands; Values for success to send commands
        """
        result = self.client.write_register(address=0x06, value=volume, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to write register", result)
            return None
        else:
            return result.registers
