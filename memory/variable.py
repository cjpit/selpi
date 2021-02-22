import struct
from memory import convert
from memory import Range

def create(arg):
    if type(arg) is str:
        return Variable(arg, MAP[arg][ADDRESS])
    if type(arg) is int:
        return Variable(address_to_name(arg), arg)
    raise NotImplementedError("Unable to create Variable from %s" % type(arg))

def address_to_name(address):
    for name in MAP.keys():
        if MAP[name][ADDRESS] == address:
            return name
    return 'Unknown'

ADDRESS = 'address'
TYPE = 'type'
DESCRIPTION = 'description'
UNITS = 'units'
CONVERSION = 'conversion'
FORMAT = 'format'
WORDS = 'words'

MAP = {
    "CommonScaleForAcVolts": {
        ADDRESS: 41000,
        TYPE: "ushort",
    },
    "CommonScaleForAcCurrent": {
        ADDRESS: 41001,
        TYPE: "ushort",
    },
    "CommonScaleForDcVolts": {
        ADDRESS: 41002,
        TYPE: "ushort",
    },
    "CommonScaleForDcCurrent": {
        ADDRESS: 41003,
        TYPE: "ushort",
    },
    "CommonScaleForTemperature": {
        ADDRESS: 41004,
        TYPE: "ushort",
    },
    "CommonScaleForInternalVoltages": {
        ADDRESS: 41005,
        TYPE: "ushort",
    },
    "TotalKacokWhTotalAcc": {
        DESCRIPTION: 'AC Lifetime Solar Energy',
        ADDRESS: 41519,
        TYPE: "uint",
        UNITS: "Wh",
        CONVERSION: "ac_wh",
    },
    "CombinedKacoAcPowerHiRes": {
        DESCRIPTION: 'AC Solar Power',
        ADDRESS: 0xa3a8,
        TYPE: "uint",
        UNITS: "W",
        CONVERSION: "ac_w",
    },
    "LoadAcPower": {
        DESCRIPTION: 'AC Load Power',
        ADDRESS: 41107,
        TYPE: "uint",
        UNITS: "W",
        CONVERSION: "ac_w",
    },
    "ACLoadkWhTotalAcc": {
        DESCRIPTION: 'AC Lifetime Load Energy',
        ADDRESS: 41438,
        TYPE: "uint",
        UNITS: "Wh",
        CONVERSION: "ac_wh",
    },
    "BatteryVolts": {
        DESCRIPTION: 'Battery Volts',
        ADDRESS: 0xa05c,
        TYPE: "ushort",
        UNITS: "V",
        CONVERSION: "dc_v",
    },
    "DCBatteryPower": {
        DESCRIPTION: 'Battery Power',
        ADDRESS: 0xa02f,
        TYPE: "int",
        UNITS: "W",
        CONVERSION: "dc_w",
    },
    "Shunt1Power": {
        DESCRIPTION: 'Shunt 1 Power',
        ADDRESS: 0xa088,
        TYPE: "short",
        UNITS: "W",
        CONVERSION: "dc_w",
    },
    "Shunt2Power": {
        DESCRIPTION: 'Shunt 2 Power',
        ADDRESS: 0xa089,
        TYPE: "short",
        UNITS: "W",
        CONVERSION: "dc_w",
    },
    "Shunt1Name": {
        DESCRIPTION: 'Shunt 1 Name',
        ADDRESS: 0xc109,
        TYPE: "short",
        UNITS: "",
        CONVERSION: "shunt_name",
    },
    "Shunt2Name": {
        DESCRIPTION: 'Shunt 2 Name',
        ADDRESS: 0xc10a,
        TYPE: "short",
        UNITS: "",
        CONVERSION: "shunt_name",
    },
    "BatteryTemperature": {
        DESCRIPTION: "Battery Temperature",
        ADDRESS: 0xa03c,
        TYPE: "ushort",
        UNITS: "°C",
        CONVERSION: "temperature",
    },
    "AddShunt1kWhPreviousAcc": {
        DESCRIPTION: "Shunt 1 Energy Today",
        ADDRESS: 0xa145,
        TYPE: "short",
        UNITS: "Wh",
        CONVERSION: "dc_wh",
    },
    "ACLoadkWhPreviousAcc": {
        DESCRIPTION: "AC Load Energy Today",
        ADDRESS: 0xa1cb,
        TYPE: "short",
        UNITS: "Wh",
        CONVERSION: "ac_wh",
    },
    "InverterDCkWhPreviousAcc": {
        DESCRIPTION: "???",
        ADDRESS: 0xa130,
        TYPE: "short",
        UNITS: "Wh",
        CONVERSION: "dc_wh",
    },
    "TotalKacokWhPreviousAcc": {
        DESCRIPTION: "AC Solar Energy Today",
        ADDRESS: 0xa145,
        TYPE: "short",
        UNITS: "Wh",
        CONVERSION: "ac_wh",
    },
    "BattInkWhPreviousAcc": {
        DESCRIPTION: "Battery In Energy Today",
        ADDRESS: 0xa171,
        TYPE: "uint",
        UNITS: "Wh",
        CONVERSION: "dc_wh",
    },
    "BattOutkWhPreviousAcc": {
        DESCRIPTION: "Battery Out Energy Today",
        ADDRESS: 0xa18c,
        TYPE: "uint",
        UNITS: "Wh",
        CONVERSION: "dc_wh",
    },
    "BattSocPercent": {
        DESCRIPTION: "Battery State of Charge",
        ADDRESS: 41089,
        TYPE: "ushort",
        UNITS: "%",
        CONVERSION: "percent",
    },
    "LoginHash": {
        ADDRESS: 0x1f0000,
        TYPE: ""
    },
    "LoginStatus": {
        ADDRESS: 0x1f0010,
        TYPE: "ushort"
    },
    "StateOfChargeShutdown": {
        DESCRIPTION: 'Whether SoC shutdown is enabled (1 = true)',
        ADDRESS: 0xc082,
        TYPE: "ushort",
        UNITS: '%',
    },
    "StatOfChargeShutdownSoC": {
        DESCRIPTION: 'State of Charge at which inverter will shutdown',
        ADDRESS: 0xc071,
        TYPE: "ushort",
        UNITS: '%',
    },
}

TYPES = {
    "ushort": {
        FORMAT: "<H",
        WORDS: 1,
    },
    "short": {
        FORMAT: "<h",
        WORDS: 1,
    },
    "uint": {
        FORMAT: "<I",
        WORDS: 2,
    },
    "int": {
        FORMAT: "<i",
        WORDS: 2,
    },
}

class Variable:
    def __init__(self, name: str, address: int, bytes: bytes=b'\x00\x00'):
        self.__name = name
        self.__address = address
        self.__bytes = bytes

    def get_name(self):
        return self.__name

    """
    Get the memory range for this variable
    """
    @property
    def range(self):
        return Range(self.__address, TYPES[self.get_type()][WORDS])

    def get_type(self):
        if not self.__name in MAP:
            return 'ushort'
        return MAP[self.__name][TYPE]

    """
    Set the internal bytes
    """
    @property
    def bytes(self):
        return self.__bytes

    @bytes.setter
    def bytes(self, bytes):
        self.__bytes = bytes

    """
    Get the converted value
    """
    def get_value(self, scales: dict):
        if not self.is_known():
            raise Exception("Can not convert value for unknown variable type")
        mem_info = MAP[self.__name]
        type_info = TYPES[self.get_type()]
        format = type_info["format"]
        unscaled = struct.unpack(format, self.__bytes)[0]
        if not CONVERSION in mem_info:
            return unscaled
        return convert(mem_info[CONVERSION], unscaled, scales)

    def is_known(self):
        return self.__name in MAP
