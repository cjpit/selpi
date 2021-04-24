import serial
import os
from . import Connection

class ConnectionSerial(Connection):
    def _connect(self):
        self.__port = serial.Serial(
            os.getenv('SELPI_CONNECTION_SERIAL_PORT'),
            baudrate = os.getenv('SELPI_CONNECTION_SERIAL_BAUDRATE'),
            timeout = 0.1
        )
        self.__port.flushOutput()

    def _write(self, data: bytes):
        self.__port.write(data)
        self.__port.flushOutput()

    def _read(self, length: int) -> bytes:
        return self.__port.read(length)
