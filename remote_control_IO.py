# class ModbusController(object):
#     def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=9600, parity='N',
#                  data_bits=8, stop_bits=1, timeout=0.001):
#         self.serial_port = serial_port  # Replace this with your serial port
#         self.baud_rate = baud_rate
#         self.parity = parity
#         self.data_bits = data_bits
#         self.stop_bits = stop_bits
#         self.timeout = timeout;
#
#         self.serial = serial.Serial("/dev/ttyUSB0", baud_rate)
#         self.client = ModbusSerialClient(
#             method="RTU",
#             port=self.serial_port,
#             baudrate=self.baud_rate,
#             parity=self.parity,
#             bytesize=self.data_bits,
#             stopbits=self.stop_bits,
#             timeout=self.timeout,
#             errorcheck="crc"
#         )
#
#     def connect(self):
#         try:
#             self.client.connect();
#             print("successfully connected" + self.serial_port);
#         except Exception as e:
#             print("failure to connect ,e")
#
#     def read_register(self,starting_address = 0,
#                        quantity = 1,unit = 1):
#         try:
#             result = self.client.read_holding_registers(starting_address,quantity,unit)
#             # Check if the read operation was successful
#             if not result.isError():
#                 # Extract and print the values read from the registers
#                 decoder = BinaryPayloadDecoder.fromRegisters(
#                     result.registers,
#                     byteorder=Endian.Big, wordorder=Endian.Big
#                 )
#                 print("Values read from registers:", result.registers)
#         except Exception as e:
#             print(f"Failed to read registers. Error: {result}",e)
#             raise ModbusIOException("read register error");
#     def write_register(self,starting_address = 0,
#                        twobytedata = 0,unit = 1):
#
#         builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
#         builder.add_16bit_uint(twobytedata)  # Example data, modify as needed
#         payload = builder.to_registers()
#
#         #print(payload)
#         # Send the constructed Modbus RTU message
#         try:
#             result = self.client.write_register(address=starting_address,
#                                                 value=twobytedata, unit=unit)
#         # Check if the read operation was successful
#             if not result.isError():
#                 # Extract and print the values read from the registers
#                 print("Write Operation is successful");
#         except Exception as e:
#             print("Failed to read registers. Error: ",e)
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
#     def write_coil(self, address: int, value: bool, slave_id=0, delay=0):
#         """
#         Write a coil to the modbus server.
#             self.client.write_coil(0x01, False)
#         Args:
#             address: Address to write to
#             value: Value to write to
#             slave_id: Slave id
#
#         Returns:
#
#         """
#         print(address, value, slave_id)
#         self.client.write_coil(address, value, slave=slave_id)
#
# class Standard_modbus_alarm(ModbusController):
#     def __init__(self, ModbusSever,unit = 0x01):
#         super().__init__(ModbusSever.serial_port, ModbusSever.baud_rate
#                  ,ModbusSever.parity,ModbusSever.data_bits,ModbusSever.stop_bits,ModbusSever.timeout)  # Calling the Parent class's __init__ method
#         self.unit = unit;
#     def alarmVolumeSet(self,volume = 15):
#         try:
#             self.write_register(starting_address=0x04,twobytedata=volume,unit = self.unit);
#             #self.read_register(starting_address=0x01,quantity=1,unit = self.unit)
#             print('volume set as ' + str(volume));
#         except ModbusIOException as e:
#             print("Wrong to set the alarm volume",e);
#
#     def alarmPlayMode(self,mode = 1):
#         try:
#             self.write_register(starting_address=9, twobytedata=mode, unit=self.unit);
#         except ModbusIOException as e:
#             print("Wrong to set the alarm play mode",e)
#
#     def setAlarmAddress(self,unit):
#         try:
#             self.write_register(starting_address=0x0B, twobytedata=unit, unit=self.unit);
#             self.unit = unit;
#         except:
#             print("Wrong to assign uint ID to alarm device");
#
#     def playAlarm(self):
#         try:
#             request = self.write_register(starting_address= 1, twobytedata= 1, unit=self.unit);
#             print('start to play alarm');
#             self.write_bytes('EF AA 01 AA 02 00 AC EF 55');
#         except Exception \
#                 as e:
#             print("Failure to let alarm play",e);
#
#     def stopAlarm(self):
#         try:
#             self.write_register(starting_address=2, twobytedata= 1, unit=self.unit);
#             self.write_bytes('EF AA 01 AA 02 00 AC EF 55');
#             print('stop playing alarm');
#         except Exception as e:
#             print("Failure to let alarm stop",e);
#
#     def check_configuration(self):
#         # check the configuration
#         self.serial.reset_input_buffer();
#         self.write_bytes('EF FF FF A6 33 EF 55');
#         result = self.serial.read(10);
#         print(['{:02x}'.format(b) for b in result])
#         # self.client.close();
#         # time.sleep(1);
#         # self.client.connect();
#     def reset_alarm(self):
#         # reset the alarm as default setting
#         self.serial.reset_input_buffer();
#         self.write_bytes('EF FF FF A7 33 EF 55');
#         result = self.serial.read(7);
#         print(['{:02x}'.format(b) for b in result])
#         self.client.close();
#         time.sleep(1);
#         self.client.connect();


from pymodbus.client import ModbusSerialClient
import numpy as np
from RS485 import *


def convert_16bits_integer(np_binary_array):
    """
    convert 16 length np.int into 16 bits data
    :param np_binary_array: 16 length long np.int
    :return: 16bits result else None for Failure
    """
    if len(np_binary_array) != 16:
        return None
    low_8bits = np.packbits(np_binary_array[:8])
    high_8bits = np.packbits(np_binary_array[8:])
    print(low_8bits)
    print(high_8bits)
    return high_8bits << 8 | low_8bits


# serial_port="/dev/ttyUSB0", baud_rate=19200, parity='N',
#                  data_bits=8, stop_bits=1, timeout=0.01,
# ModbusSerialClient(
#             method='rtu',
#             Framer=Framer.RTU,
#             port=self.serial_port,
#             baudrate=self.baud_rate,
#             parity=self.parity,
#             bytesize=self.data_bits,
#             stopbits=self.stop_bits,
#             timeout=self.timeout,
#             errorcheck="crc"
#         )
class zhongsheng_io_relay_controller(RS485):
    def __init__(self, serial_client: ModbusSerialClient, unit=0x01, small_port=True):
        """
        :param serial_client: The pymodbus serial client object
        :param unit: uint16,the slave id for the device, the default value is 1
        :param small_port: bool, IO device has two categories: small port meaning 4 and less than 4 port in input or output;
        the big port meaning bigger than 4 port in input or output. True for small, False for big one
        """
        super().__init__(serial_client, unit)
        self.small_port = small_port
        self.unit = unit
        self.modes_names = ["普通模式", "联动模式", "点动模式", "开关循环模式", "", "开固定时长模式"]
        self.baud_rate_dict = {0: 4800, 1: 9600, 2: 14400, 3: 38400, 5: 56000, 6: 57600, 7: 115200}
        self.client = serial_client
        print("Connected to Modbus RTU device zhongsheng_IO_relay_controller")

    def read_input_conditions(self, address, count=1):
        """
        To read input relay conditions, 1 for high voltage detected ,0 for low voltage detected
        :param address: uint16, input_register's starting address to be read(starting address from 0000H~0034H
        :param count: uint8, quantities of registers be read
        :return: uint16 array, values of the read registers, None for failure to read
        """
        result = self.client.read_input_registers(address=address, count=count, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to read IO input relay: ", result)
            return None
        else:
            return result.registers

    def switch_single_ouput(self, address, value):
        """
        switch single relay output
        :param address: uint16, register's address to write start from 0000H to 002FH
        :param value: bool, True for turn-on and False for turn-off; The close and open
                      state depends on the wire connection.

        :return(bool): The coil's or output condition, False for failure to read the coil
                        condition
        """
        self.client.write_coil(address=address, value=value, slave=self.unit)
        result = self.client.read_coils(address=address, count=1, slave=self.unit)
        if isinstance(result, ModbusException):
            raise False
        else:
            return result.bits[0]

    # def read_output_conditions(self,address = 0,count = 1):
    #     '''
    #     read output relays' conditions
    #     :param address: the
    #     :return:
    #     '''
    #     result = self.client.read_discrete_inputs(address = address,count=count,slave = self.unit);
    #     if isinstance(result, ModbusException):
    #         print("Failure to read output conditions", result);
    #         return None;
    #
    #     else:
    #         return result.bits[0];

    def read_outputs(self, address=0, count=1):
        """
        read the output relay coils
        :param count:
        :param address:  uint16, register's address to be read
        :return: None or list, when there is a response on device,a list of relays' condition is return
                otherwise, None is return
        """
        result = self.client.read_coils(address=address, count=count, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to read IO outputs ", result)
            return None
        else:
            return result.bits

    def control_switches(self, open_switch_list, close_switch_list):
        """
        control all switch at the same time based on open_witch_list and close_switch_list
        openlist represents True to switches and closelist represents False to switches
        :param open_switch_list: list of outputs' number to switch to open
        :param close_switch_list: list of outputs' number to switch to close
        :return: bool, True for success to write; False for failure to write
        """
        result = self.client.read_holding_registers(address=0x0035, count=3, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to read switches' conditions: ", result)
            return False

        original_switches_conditions = []
        print(result.registers)
        for i, value in enumerate(result.registers):
            temp = bin(value)[2:]
            fixed_length_binary = list('0' * (16 - len(temp)) + temp)
            fixed_length_binary.reverse()
            original_switches_conditions = original_switches_conditions + fixed_length_binary
        new_switches_conditions = original_switches_conditions

        for value in open_switch_list:
            new_switches_conditions[value - 1] = '1'
        for value in close_switch_list:
            new_switches_conditions[value - 1] = '0'

        values = np.zeros(3).astype(int)
        new_switches_conditions = np.array(new_switches_conditions, dtype=int)
        low_2bytes = new_switches_conditions[0:16]
        mid_2bytes = new_switches_conditions[16:32]
        high_2bytes = new_switches_conditions[32:48]
        values[0] = convert_16bits_integer(low_2bytes)
        values[1] = convert_16bits_integer(mid_2bytes)
        values[2] = convert_16bits_integer(high_2bytes)

        result = self.client.write_registers(address=0x0035, values=list(values), slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to control switches' conditions: ", result)
            return False
        return True

    def set_all_switches(self, set):
        """

        :param set: 0 or 1,set all swiches' relay open or close simutaneously
        :return: bool, True for success False for failure
        """
        if self.small_port:
            result = self.client.write_register(address=0x000C, value=set, slave=self.unit)
        else:
            result = self.client.write_register(address=0x0034, value=set, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to set_all_switches ", result)
            return False
        else:
            print("Success to set all switches as " + str(set))
            return True

    'setting holding registers'
    """
    To set switch modes
    values : 01 普通模式
             02 联动模式
             03 点动模式
             04 开关循环模式
             05 开固定时长模式
             
             一共有48个通道地址：0096H ~00C6H
    """

    def set_switch_mode(self, address=0, mode=1):
        """
        To set switch mode and the mode details are above description and the manual file
        :param address: uint16, starting address of holding register (0096H~00C6H)
        :param mode: integer from (1 to 5), five mode to be chosen
        :return:bool, True for success False for failure
        """
        if 1 > mode > 5:
            print("Failure to set mode: mode should be integer between 1 and 5")
            return

        result = self.client.write_register(address=address, value=mode, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to set switch mode", result)
            return False
        else:
            print("set tunnel " + str(address) + " as mode " + self.modes_names[mode])
            return True

    def set_all_switch_mode(self, mode):
        """
        To set all switches' mode
        :param mode: integer from (1 to 5), five mode to be chosen
        :return:bool, True for success False for failure
        """
        if 1 > mode > 5:
            print("Failure to set mode: mode should be integer between 1 and 5")
            return;
        result = self.client.write_registers(address=0, count=48, values=mode, slave=self.unit)
        if isinstance(result, ModbusException):
            print("Failure to set all switch mode ", result)
            return False
        else:
            print("Success to set all switch mode as " + self.modes_names[mode])
            return True

    def set_automatic_submit_inputs_condition(self, mode):
        '''
        Set input condition automatically send to port, not be tested
        :param mode:
        :return:
        '''
        if self.small_port:
            result = self.client.write_register(address=9, value=mode, slave=self.unit)
        else:
            result = self.client.write_register(address=0x0031, value=mode, slave=self.unit)
        if isinstance(result, ModbusException):
            return False
        else:
            print("Success to set automatically submit mode")
            return True

    def set_controller_address(self, unit=-1, baud_rate=-1):
        '''
        set slave id and baud_rate for IO_relay
        :param unit: uint8, slave id
        :param baud_rate: integer from 0 to 5, baurd rate choice
        :return: bool, True for success vice versa
        '''
        result = ModbusException(Exception)
        if self.small_port:
            if 0 <= baud_rate <= 7:
                result = self.client.write_register(address=0x000B, value=baud_rate, slave=self.unit)
            if 0 < unit < 0xFF and self.unit != unit:
                result = self.client.write_register(address=0x000A, value=unit, slave=self.unit)

        else:
            if 0 <= baud_rate <= 7:
                result = self.client.write_register(address=0x0033, value=baud_rate, slave=self.unit)
            if 0 < unit < 0xFF and self.unit != unit:
                result = self.client.write_register(address=0x0032, value=unit, slave=self.unit)

        if isinstance(result, ModbusException):
            print("Failure to set slave id or baudrate")
            return False
        print("Success to set slave id and baudrate: restarting...........")
        self.client.close()
        print("Done")
        return True