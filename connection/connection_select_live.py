from ssl import SSLZeroReturnError
from exception import ConnectionLostException, ValidationException
import settings
from . import Connection
from .ssl import create_ssl_connection

class ConnectionSelectLive(Connection):
    def __init__(
            self,
            create_ssl_connection_function: create_ssl_connection=None,
            username: bytes=None,
            password: bytes=None,
            device: bytes=None

    ):
        super().__init__()
        self.__create_ssl_connection = create_ssl_connection_function or create_ssl_connection
        self.__username = username or settings.getb(b'CONNECTION_SELECT_LIVE_USERNAME')
        self.__password = password or settings.getb(b'CONNECTION_SELECT_LIVE_PASSWORD')
        self.__device = device or settings.getb(b'CONNECTION_SELECT_LIVE_DEVICE')
        self.__socket = None
        self.__write_failures = 0

    def _connect(self):
        hostname = b'select.live'
        port = 7528
        self.__socket = self.__create_ssl_connection(hostname, port)

        response = self._read(1024)
        if response != b'LOGIN\r\n':
            raise ValidationException(
                "Authentication failed, 'LOGIN' prompt was missing, received %s instead"
                % response
            )
        self._write(b'USER:'+self.__username+b':'+self.__password+b'\r\n')
        response = self._read(1024)
        if response != b'OK\r\n':
            raise ValidationException(
                "Authentication failed, username or password not accepted, received %s"
                % response
            )

        self._write(b'CONNECT:'+self.__device+b'\r\n')
        response = self._read(1024)
        if response != b'READY\r\n':
            raise ValidationException(
                "Authentication failed, device not accepted, received %s"
                % response
            )

    def _read(self, length: int):
        return self.__socket.read(length)

    def _write(self, data: bytes):
        if self.__write_failures > 3:
            raise ConnectionLostException("Too many sequential write failures (%s)" % self.__write_failures)
        try:
            response = self.__socket.write(data)
        except SSLZeroReturnError:
            self.__write_failures = self.__write_failures + 1
            self._connect()
            return self._write(data)
        self.__write_failures = 0
        return response
