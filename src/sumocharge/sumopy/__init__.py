""" Bare-bones Parrot Jumping Sumo control.
"""
import collections
import json
import socket
import struct
import threading
import time
import SocketServer


# Motor commands must be at 40 Hz for video to work.
MOTOR_HZ = 40.0


def hex_repr(data):
    """ Pretty-print binary data.
    """
    return ''.join('\\x{:02x}'.format(ord(c)) for c in data)


class SumoController(object):
    """ Parrot Jumping Sumo controller.
    """
    def __init__(self, sumo_ip='192.168.2.1', init_port=44444, d2c_port=54321,
                 debug=False):
        """ Set up the instance.
        """
        self._sumo_ip = sumo_ip
        self._sequence = 1
        self._debug = debug
        self._d2c_port = d2c_port

        # Do the init handshake, gathering a c2d_port and the size of the
        # video packets.
        self._c2d_port, vid_data_size = self._do_init(init_port)

        # Create the socket that we'll send data to the sumo via
        self._c2d_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Create and start the threaded listen server. Video packets are
        # larger than the default UDPServer size so we set max_packet_size
        # appropriately.
        class UDPHandler(SocketServer.BaseRequestHandler):
            """ Handler for incoming UDP data.
            """
            def handle(self):
                print hex_repr(self.request[0][:25])

        self._d2c_server = SocketServer.UDPServer(('', d2c_port), UDPHandler)
        self._d2c_server.max_packet_size = vid_data_size
        threading.Thread(target=self._d2c_server.serve_forever).start()

        # Create and start the 40Hz movement sender. This keeps the connection
        # "alive".
        self._movement_commands = collections.deque()
        threading.Thread(
            target=self._motor_thread,
            args=(self._movement_commands,)
        ).start()

    def _do_init(self, init_port=44444):
        """ Do the init handshake, return the c2d_port.
        """
        init_msg = {
            'controller_name': 'SumoPy',
            'controller_type': 'Python',
            'd2c_port': self._d2c_port,
        }
        init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        init_sock.connect((self._sumo_ip, init_port))
        init_sock.sendall(json.dumps(init_msg))

        # Grab the JSON respone, strip trailing \x00 to keep it valid.
        init_resp = init_sock.recv(1024)[:-1]
        json_init_resp = json.loads(init_resp)

        c2d_port = json_init_resp['c2d_port']
        if c2d_port == 0:
            raise Exception('Client already connected!')

        return c2d_port, json_init_resp['arstream_fragment_size']

    def _motor_thread(self, command_list):
        """ Drive the motors - either from commands list or stop.

            Commands are sent at 40Hz.
        """
        while True:
            try:
                cmd = command_list.popleft()
            except IndexError:
                cmd = self._move_cmd(0, 0)
            self._send(cmd)
            time.sleep(1.0 / MOTOR_HZ)

    def _send(self, cmd):
        """ Send via the c2d_port.
        """
        if self._debug:
            print '>', hex_repr(cmd)
        self._c2d_sock.sendto(cmd, (self._sumo_ip, self._c2d_port))
        self._sequence = (self._sequence + 1) % 256

    @staticmethod
    def fab_cmd(ack, channel, seq, project, _class, cmd, args):
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

        # Padded 0x00
        arr.append(0)

        # arguments, pre-packed using struct
        arr += args

        # update message length value
        arr[3] = len(arr)

        return str(arr)

    def move(self, speed, turn=0, duration=1.0, block=True):
        """ Move in a manner, for a duration(seconds).
        """
        # Minimum duration is one 40th of a second.
        duration = max(1.0 / MOTOR_HZ, duration)
        cmd = self._move_cmd(speed, turn)
        repetitions = int(duration * MOTOR_HZ)
        self._movement_commands.extend([cmd] * repetitions)
        if block:
            time.sleep(duration)

    def _move_cmd(self, speed, turn):
        """ Create movement commands.
        """
        cmd = SumoController.fab_cmd(
            2,  # No ACK
            10,  # Piloting channel?
            self._sequence,
            3,  # Jumping Sumo project id = 3
            0,  # Piloting = Class ID 0
            0,  # Command index 0 = PCMD
            struct.pack(
                '<Bbb',  # u8, i8, i8
                1,  # Touch screen = yes
                speed,   # -100 -> 100 %
                turn,    # -100 -> 100 = -360 -> 360 degrees
            )
        )
        return cmd

    def store_pic(self):
        """ Take a pic to internal storage - use FTP to retrieve if you want.
        """
        cmd = SumoController.fab_cmd(
            4,  # ACK
            11,  # Media channel ?
            self._sequence,
            3,  # Jumping Sumo project id = 3
            6,  # class = MediaRecord
            0,  # Command = Picture (offset 0)
            struct.pack(
                '<B',  # u8
                0,  # Internal storage = 0
            )
        )
        self._send(cmd)

    def get_pic(self):
        """ Return the last pic from the video stream.
        """
        pass


if __name__ == '__main__':

    controller = SumoController(debug=True)
    controller.move(100)
    controller.store_pic()
    controller.move(-100)
    controller.get_pic()
