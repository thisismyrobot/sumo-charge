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
        return self._packet.execute(self._io).data
