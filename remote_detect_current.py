

import serial
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import numpy as np
from RS485 import *
def convert_16bits_integer(np_binary_array):
    '''
    covert 16 binary np.int into a uint16 data
    :param np_binary_array: 16 length long np.int
    :return:
    '''
    low_8bits = np.packbits(np_binary_array[:8]);
    high_8bits = np.packbits(np_binary_array[8:]);
    print(low_8bits)
    print(high_8bits);
    return high_8bits << 8 | low_8bits;


class fengkong_current_detector(RS485):
    def __init__(self, seria_client: ModbusSerialClient, unit=0x01):
        '''
        fengkong current detector
        :param serial_port:'string, the port to be read
        :param baud_rate: baud_rate to be set and the choice based on manual file
        :param parity: char,default as 'N' None
        :param data_bits: default 8 bits represent data
        :param stop_bits: default 1 bit for stop bit
        :param timeout:float, default 0.01 and too small cause problem
        :param unit: uint16,the slave id for the device, the default value is 1
        '''
        super().__init__()
        self.baud_rate_dict = {3:1200,4:2400,5:4800,6:9600,7:19200}
        self.unit = unit;
        self.client = seria_client;

        print("Connected to Modbus RTU device " + "fengkong_current_detector");

    def set_controller_address(self, unit=-1, baud_rate=-1):
        '''
        set slave id and baud_rate for IO_relay
        :param unit: uint8,uint8, slave id
        :param baud_rate: integer from 3 to 7, baurd rate choice
        :return: bool, True for success vice versa
        '''

        if 3 <= baud_rate <= 7:
            result = self.client.write_registers(address=0x20, values=baud_rate, slave=self.unit);
            if isinstance(result, ModbusException):
                print("Failure to set baudrate",result)
                return False;

        if 0 < unit < 0xFF and self.unit != unit:
            result = self.client.write_registers(address=0x57, values=unit, slave=self.unit);
        print("Success to set slave id and baudrate: restarting..........");
        self.client.close();
        # try:
        #     connection = self.client.connect();
        #     if connection:
        #         print("Connected to Modbus RTU device");
        #     else:
        #         print("Failure to do connection ")
        # except Exception as e:
        #     print(e);
        print("Done")
        return True;
    def read_current(self):
        '''
        Reads the current in ampere
        :return:
        '''
        result = self.client.read_holding_registers(address=0x0056, count=1, slave=self.unit);
        if isinstance(result, ModbusException):
            print("Fail to read current",result)
            return None;
        else:
            return result.registers[0]*(20-0)/10000-0;


    def close(self):
        self.client.close();

    def connect(self):
        self.client.connect();



