# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pymodbus.client import ModbusSerialClient

from RS485 import *




class ModbusAlarm(RS485):
    def __init__(self, serial_client: ModbusSerialClient,name, unit=0x01):
        """

        :param serial_client: pymodbus serialclient object
        :param unit: the slave id for this device
        """
        super().__init__(serial_client, unit)
        self.unit = unit
        self.client = serial_client
        self.name = name
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

    def check(self):
        '''
        check if device is connected
        :return: True for connected, False for disconnected
        '''
        return super().check_connection(addr=0x01)