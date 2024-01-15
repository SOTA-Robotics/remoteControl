'''
reg way to extract information
'''
# def decode_logging_information():
#     log_data = ["2023-01-08 19:45:00 - ERROR - This is an error message"];
#     log_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - \w+ - (.*)');
#     for line in log_data:
#         match = log_pattern.match(line);
#         print(line);
#         if match:
#             message = match.group(1);
#             print(f"Extracted Message :{message}")
#         else:
#             print("No match")


'''
json format to log the informaiton
'''
# def write_read_json_logging_information():
#     # json_data_1 = {"key1": "value1", "key2": 42};
#     # json_data_2 = {"key1":["apple","banana"]};
#     # file_path = 'json_log.log'
#     # logging.basicConfig(filename=file_path, level=logging.INFO);
#     # logger = logging.getLogger("test_logger");
#     # json_data = json.dumps(json_data_1)
#     # print(json_data)
#     # logger.error(f"{json_data}");
#     with open('json_log.log','r') as file:
#         log_data = file.readlines();
#     log_data = log_data[-1];
#     json_string = log_data.split("ERROR:test_logger:")[-1].strip();
#     decoded_data = json.loads(json_string);
#
#     print("Decoded Data :", decoded_data);
#     print(decoded_data["key1"]);
#     print(decoded_data["key2"]);
#
#
#
# '''
# write logging information in a log file
# '''
#
# def write_logging_information():
#     log_format = ('');
#     logging.basicConfig(filename = 'my_log_file.log',level=logging.INFO, format=log_format);
#     logger = logging.getLogger();
#
#     logger.error("This is an error")
#
#
# '''
# read the latest new line in the logging file
# '''
# def read_latest_logging_information():
#     log_file_path = "my_log_file"
#     with open(log_file_path,'r') as file:
#         lines = file.readlines();
#
#     if lines:
#         last_line = lines[-1];
#         print("last line in the log file:",last_line);
#     else:
#         print("log file is empty or does not exist")


'''
abandomed alarm class
'''
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

'''

'''
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
