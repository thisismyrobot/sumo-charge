""" Bare-bones Parrot Jumping Sumo control.
"""
import json
import socket


class SumoController(object):
    """ Parrot Jumping Sumo controller.
    """
    def __init__(self, ip='192.168.2.1', init_port=44444):
        self._ip = ip
        self._init_port = init_port

    def connect(self):
        c2d_port = self.get_c2dport()
        print c2d_port

    def get_c2dport(self, d2c_port=54321):
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


if __name__ == '__main__':
    controller = SumoController()
    controller.connect()
