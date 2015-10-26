""" Local controller for Jumping Sumo

    Intended to be used by the www.py Web interface.
"""
import sumopy
import threading
import time
import SocketServer


class C2DMessages(object):
    """ The messages available for sending to the Sumo.
    """
    Enable = 'enable_controller'
    Disable = 'disable_controller'


def start_server(state_dict):
    """ Start a UDP server and update the state dict as commanded via messages
        to it.
    """
    class Handler(SocketServer.BaseRequestHandler):
        """ Handle all messages.
        """
        def handle(self):
            data = self.request[0]
            if data == C2DMessages.Enable:
                state_dict['enabled'] = True
                print 'Enabling Local Client'
            elif data == C2DMessages.Disable:
                state_dict['enabled'] = False
                print 'Disabling Local Client'

    server = SocketServer.UDPServer(('0.0.0.0', 8001), Handler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()


def main():
    """ Attempt to control the sumo.
    """
    state = {
        'enabled': False,
    }

    start_server(state)

    while True:
        if state['enabled']:
            controller = sumopy.SumoController(
                sumo_ip='127.0.0.1'
            )

            while state['enabled']:
                controller.move(10, 0, 0.1)
                time.sleep(1)

        time.sleep(1)


if __name__ == '__main__':
    import multiprocessing

    while True:
        proc = multiprocessing.Process(target=main)
        proc.start()
        proc.join()
        proc.terminate()
        print 'Restarting...'
        time.sleep(5)
