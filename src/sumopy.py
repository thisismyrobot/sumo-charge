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

        return json.loads(init_resp)['c2d_port']

    def _send(self, cmd):
        """ Send via the c2d_port.
        """
        print '> ', repr(cmd)
        self._c2d_sock.sendall(cmd)
        self._sequence = (self._sequence + 1) % 256

    @staticmethod
    def fab_cmd(class_id, seq, idx, *args):
        arr = bytearray()

        # Class Id?
        arr.append(class_id)

        # boilerplate?
        arr.append(0xa)

        # Sequence number
        arr.append(seq)

        # boilerplate?
        arr.append(0)  # becomes total length
        arr.append(0)
        arr.append(0)
        arr.append(0)

        # count of args?
        arr.append(len(args))

        # boilerplate?
        arr.append(0)
        arr.append(0)

        # Command index?
        arr.append(idx)

        # arguments
        map(arr.append, args)

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
            2,  # Class 2?
            self._sequence,
            0,  # Command index 0 = PCMD
            1,  # Touch screen = yes
            speed,  # -100 -> 100 %
            turn,  # -100 -> 100 = -360 -> 360 degrees
        )
        self._send(cmd)

    def stop(self):
        self.move(0, 0)


if __name__ == '__main__':
    controller = SumoController()
    controller.connect()
    controller.move(20)
    time.sleep(0.1)
    controller.stop()
