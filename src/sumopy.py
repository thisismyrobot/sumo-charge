""" Bare-bones Parrot Jumping Sumo control.
"""
import json
import socket
import time


class SumoController(object):
    """ Parrot Jumping Sumo controller.
    """
    def __init__(self, ip='192.168.2.1', init_port=44444):
        self._ip = ip
        self._init_port = init_port
        self._connected = False
        self._sequence = 1

    def _get_c2dport(self, d2c_port=54321):
        """ Return the ports we need to connect to for control.
        """
        init_msg = {
            'controller_name': 'SumoPy',
            'controller_type': 'Python',
            'd2c_port': d2c_port,
        }
        init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        init_sock.connect((self._ip, self._init_port))
        init_sock.sendall(json.dumps(init_msg))

        # Strip trailing \x00.
        init_resp = init_sock.recv(1024)[:-1]

#        print init_resp

        return json.loads(init_resp)['c2d_port']

    def _send(self, cmd):
        """ Send via the c2d_port.
        """
#        print '>', repr(cmd)
        self._c2d_sock.sendall(cmd)
        self._sequence = (self._sequence + 1) % 256

    @staticmethod
    def fab_cmd(ack, channel, seq, project, _class, cmd, *args):
        """ Assemble the bytes for a command.

            Most values from:
                https://github.com/Parrot-Developers/libARCommands/blob/master/Xml/common_commands.xml

            class_id:
                From "<class name="Common" id="[id]">" in Xml.

            seq:
                Incrementing command sequence number (0-255).

            idx:
                Index (zero-based) of the command in the Xml.

            https://github.com/Zepheus/ardrone3-pcap/blob/master/README.md
        """
        arr = bytearray()

        # Type: 2 = No ACK, 4 = ACK I think. See <..."buffer="NON_ACK"> in
        # XML.
        arr.append(ack)

        # Channel - 10 is for sending commands. 11 for photo trigger?
        arr.append(channel)

        # Sequence number - 0-255
        arr.append(seq)

        # Message length - we update this at end.
        arr.append(0)

        # boilerplate?
        arr.append(0)
        arr.append(0)

        # Project ID - Jumping Sumo = 3
        arr.append(0)
        arr.append(project)

        # Class ID
        arr.append(_class)

        # Command index?
        arr.append(cmd)

        # arguments
        map(arr.append, args)

        # Trailing 0x00
        arr.append(0)

        # update message length value
        arr[3] = len(arr)

        return str(arr)

    def connect(self):
        c2d_port = self._get_c2dport()
        self._c2d_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._c2d_sock.connect((self._ip, c2d_port))
        self._connected = True

    def move(self, speed, turn=0):
        cmd = SumoController.fab_cmd(
            2,  # No ACK
            10, # Piloting channel
            self._sequence,
            3,  # Jumping Sumo project id = 3
            0,  # Piloting = Class ID 0
            0,  # Command index 0 = PCMD
            1,  # Touch screen = yes
            speed,  # -100 -> 100 %
            turn,  # -100 -> 100 = -360 -> 360 degrees
        )
        self._send(cmd)

    def pic(self):
        cmd = SumoController.fab_cmd(
            4,  # No ACK
            11, # Media channel ?
            self._sequence,
            3,  # Jumping Sumo project id = 3
            6,  # class = MediaRecord
            0,  # Command = Picture (offset 0)
            0,  # Internal storage = 0
        )
        self._send(cmd)

    def stop(self):
        self.move(0, 0)


if __name__ == '__main__':

    print repr('\x02\n\x07\x0e\x00\x00\x00\x03\x00\x00\x00\x01\x14\x02')
    print repr(
        SumoController.fab_cmd(
            2,  # No ACK
            10,  # Piloting channel
            7,  # Sequence
            3,  # Jumping Sumo project id = 3
            0,  # Class 0 = Piloting
            0,  # Command = PCMD (offset 0)
            1,  # Touch screen = yes
            20,  # -100 -> 100 %
            2,  # -100 -> 100 = -360 -> 360 degrees
        )
    )

    print repr('\x04\x0b\x07\x0c\x00\x00\x00\x03\x06\x00\x00\x00')
    print repr(
        SumoController.fab_cmd(
            4,  # No ACK
            11,  # Media channel ?
            7,  # Sequence
            3,  # Jumping Sumo project id = 3
            6,  # Class 6 = MediaRecord
            0,  # Command = Picture (offset 0)
            0,  # Internal storage = 0
        )
    )


    controller = SumoController()
    controller.connect()
    controller.move(20)
    controller.pic()
    time.sleep(0.1)
    controller.stop()
