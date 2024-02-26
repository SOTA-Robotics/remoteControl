# remoteControl

This remote control system is designed for handling any emergencies including power-off, and exceptions such as 
robot conveyors conducting wrong operations, which will potentially damage the system itself or the people's 
safety. Hence a remote control system is proposed to prevent this happening and monitor the whole system if works
properly. If any exceptions occur, the system will be aborted and record any wrong message in the "logging.log" file.

# Here are descriptions for the remote control system
## communication
1. Main system(Computer vision system): This system is required to communicate with the main system which is in charge of detecting and commanding a delta robot to sort 
                                        materials.  The communication is via socket and it requires rj45 as well as routing connection. The message's format is defined as
                                        a dictionary of {"temp_dict": temperature_dict, "count_dict": self.grasp_count_dict, "conveyor": True, "robot_error": self.robot_error,
                                                            "start": False, "pause": False, "stop": False}
2. RS485 for slave devices(current sensor, alarm and relays):  This communication is based on Modbus protocol and RS485 physical connection.

## Finite State Machine(FSM)
The functionality of this system is implemented by simple FSM with three states Start, Waiting, and Stop.
The System is required to obey rules and the rules are coded in FSM

## Exception code list
Exception Code | Explain | Hanle
------------ | ------------- | -------------
0x501 | Failure connection between the control system and the main system | Warning
0x502 | Failure to open RS485 port  | Warning
0x503 | The control system has not received the main system message after an amount of time | Stop&Warning
0x5A0~ | devices' connections failure | Warning
0x401 | Temperature exceed the threshold | Warning
0x402 | Robot exception | Stop&Warning
0x403 | Conveyor exception | Stop&Warning
0x404 | Current exception | Stop&Warning


## Information Format
Name | type | Example
------------ | ------------- | -------------
temp_dict | dict | [ "intake_1": tmp(float), "intake_2":tmp(float), "outlet_1":tep((float), "outlet_2":tmp(float)]
count_dict | dict | ["class_type1": count_num1, "class_type1": count_num2]
conveyor | boolean | True
robot_error | int | 0
start | boolean | False
pause | boolean | False
stop | boolean | False

# Usage of the remote control system 
The system is to monitor the state of the system and communication is crucial. To set up and let the system work. Serval configurations are important
All configurations are amended in YAML file

devices.yaml: devices that are accessed by RS485, devices' name, and their slave ID
package.yaml: configurations include relays' number of each device, temperature threshold, etc
RS485_config.yaml: define the port configurations such as baudrate, port, and connection, etc
socket_config.yaml: define socket configurations such as host, port, etc

Ensure physical connections are intact before setting the connection as True in the configuration's file.
