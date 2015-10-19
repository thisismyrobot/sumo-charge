""" Will find and return you a USB serial port (if you have one :D).
"""
import serial
import serial.tools.list_ports


def first(baud=9600):
    try:
        port = (p[0]
                for p
                in serial.tools.list_ports.comports() if 'USB' in p[1]).next()
    except StopIteration:
        raise Exception('No USB COM ports!')

    try:
        return serial.Serial(port, baud, timeout=1)
    except:
        raise Exception('Failed to open \'{}\'!'.format(port))
