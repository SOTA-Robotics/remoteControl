class Thermometer(object):
    def __init__(self, config_name="thermometer"):
        self.config = load_omega_config(config_name)
        self._port_number_list = self.config["port_number_list"]
        self._port_name_list = self.config["port_name_list"]
        assert len(self._port_number_list) == len(self._port_name_list)

        self.client = ModbusSerialClient(
            self.config["address"],
            baudrate=self.config["baud_rate"],
            parity="N",
            timeout=0,
        )

        self.client.connect()
        self.serial = serial.Serial(
            self.config["address"], baudrate=self.config["baud_rate"]
        )

    def write_bytes(self, hex_bytes):
        """
        Write a bytes to the modbus server.
        self.write_bytes("02 06 00 02 00 01 E9 F9")
        Args:
            hex_bytes:

        Returns:

        """
        byte = bytes.fromhex(hex_bytes)
        self.serial.write(byte)

    @staticmethod
    def hex_2_bit(hex):
        # Convert each byte to binary
        binaries = [bin(b)[2:].zfill(8) for b in hex]

        # Combine every two binary strings into one
        combined_binaries = [
            binaries[i] + binaries[i + 1] for i in range(1, len(binaries), 2)
        ]

        # Convert each combined binary string to decimal
        decimals = [int(b, 2) for b in combined_binaries]

        # Print the decimals
        return decimals

    def get_temperature_dict(self):
        """Get the temperatures of specified sensors as a dict.

        Returns:
            specified_temperature_dict: The unit is degree centigrade.
        """
        # send the get temperature command
        self.write_bytes("01 04 00 00 00 10 F1 C6")

        # read the response
        hex_value = self.serial.read(37)

        # convert the hex value to binary value
        temperature_list = self.hex_2_bit(hex_value)

        # get the temperature of the specific sensor
        specified_temperature_dict = {}
        for name, port_number in zip(self._port_name_list, self._port_number_list):
            if port_number not in range(1, 9):
                raise ValueError("The port number should be in the range of 1-8")
            specified_temperature_dict[name] = temperature_list[port_number] / 10
        return specified_temperature_dict
