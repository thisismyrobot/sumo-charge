""" Read Mifare tags.
"""
import rdm880
import serial
import serial.tools.list_ports
import sys
import time


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

# Formulate a Mifare "Get Serial number" packet. Data is "Request Idle" and
# "Do not need to execute halt command."
# Ref: http://neophob.com/files/rfid/PROTOCOL-821-880%20_2_.pdf
r = rdm880.Packet(rdm880.Mifare.GetSNR, [0x26, 0])

while True:

    # Send the packet
    reply = r.execute(io)

    # Parse the serial number
    serial = reply.data

    if serial != []:
        print serial

    time.sleep(1)
