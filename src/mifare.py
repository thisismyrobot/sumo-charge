""" Read Mifare tag serial numbers.
"""
import rdm880


class RFID(object):

    def __init__(self, io):
        self._io = io

        # Formulate a Mifare "Get Serial number" packet. Data is "Request
        # Idle" and "Do not need to execute halt command."
        # Ref: http://neophob.com/files/rfid/PROTOCOL-821-880%20_2_.pdf
        self._packet = rdm880.Packet(rdm880.Mifare.GetSNR, [0x26, 0])

    def serial(self):
        """ Return a serial number as a list of integers.
        """




# Get the first USB COM port and open it
try:
    port = (p[0]
            for p
            in serial.tools.list_ports.comports() if 'USB' in p[1]).next()
except StopIteration:
    sys.stderr.write('No USB COM ports!')
    sys.exit(1)

try:
    io = serial.Serial(port, 9600, timeout=1)
except:
    sys.stderr.write('Failed to open \'{}\'!'.format(port))
    sys.exit(1)



# Set up the module-level function
def read():
    return r.execute(io).data
