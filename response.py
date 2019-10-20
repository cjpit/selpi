import struct
from crc import CRC
from request import Request
from error import ValidationError

class Response:
    def __init__(self, request: Request):
        self.__request = request
        self.__message = bytes()

    def get_message(self) -> bytes:
        return self.__message

    def expected_length(self) -> int:
        return sum([
            len(self.__request.get_message()),     # request message
            (self.__request.get_length() + 1) * 2, # memory requested
            2,                                 # crc
        ])

    def valid(self) -> bool:
        try:
            self.validate()
        except ValidationError:
            return False
        return True

    def validate(self):
        self.validate_length()
        self.validate_crc()

    def validate_length(self):
        actual = len(self.__message)
        expected = self.expected_length()
        if actual == expected:
            return
        raise ValidationError(
            "Incorrect data length (%(actual)i of %(expected)i bytes)"
            % {'actual': actual, 'expected': expected}
        )

    def validate_crc(self):
        crc = CRC(self.__message)
        if crc.as_int() == 0:
            return
        raise ValidationError(
            "Incorrect CRC (0x%(crc)s)" \
            % { 'crc': crc.as_hex().decode("utf-8") }
        )

    def set_message(self, message: bytes):
        self.__message = message

    """
    Get the memory that the SP PRO returned
    TODO: does this make sense for write requests?
    """
    def memory(self) -> bytes:
        self.validate()
        query_length = len(self.__request.get_message())
        memory_length = (self.__request.get_length() + 1) * 2
        start = query_length
        end = start + memory_length
        return self.__message[start:end]
