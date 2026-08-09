from memory import Protocol
from memory import extract, Data, reduce
from memory.variable import TYPES, MAP
import struct
import logging

"""
Muster collects multiple requests for variables, dispatches the queries and
returns updated variables
"""
class Muster:
    def __init__(self, protocol: Protocol=None):
        self.__protocol = protocol or Protocol()

    """
    Query the wire protocol for a list of Variables and update the values in the
    variables
    """
    def update(self, variables: list):
        self.__protocol.login()
        ranges = []
        datas = []
        for var in variables:
            ranges.append(var.range)
        for range in reduce(ranges):
            logging.debug("query: %s" % range)
            res = self.__protocol.query(range)
            datas.append(Data(range, res))
        for var in variables:
            var.bytes = extract(var.range, datas).bytes

    """
    Write a value to a variable in the SP Pro memory
    """
    def write(self, name: str, value: int):
        self.__protocol.login()
        if name not in MAP:
            raise ValueError("Unknown variable: %s" % name)
        var_info = MAP[name]
        type_info = TYPES[var_info['type']]
        fmt = type_info['format']
        data = struct.pack(fmt, value)
        logging.debug("write: %s = %s" % (name, value))
        self.__protocol.write(var_info['address'], data)
