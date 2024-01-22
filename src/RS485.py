from pymodbus.exceptions import ModbusException


class RS485(object):
    def __init__(self, client, unit):
        self.client = client
        self.unit = unit

    def check_connection(self, addr):
        """
        Reading a holding register from device and check if the connection is fine or not
        :param addr:  holding_register address
        :return:
        """

        result = self.client.read_holding_registers(address=addr, count=1, slave=self.unit)
        if isinstance(result, ModbusException):
            print(f"Failure to connect  {self.__class__.__name__}")
            return False
        else:
            return True

    def read(self):
        pass

    def write(self):
        pass