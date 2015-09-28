""" Proxy for parrot devices.
"""
import json
import socket
import time
import threading
import zeroconf
import SocketServer


PROXY_IP = '192.168.20.3'
BOT_IP = '192.168.2.1'
BOT_INIT_PORT = 44444
SERVICE_NAME = '_arsdk-0902._udp.local.'
RECV_MAX = 10240

BOT_C2DPORT = None
BOT_D2CPORT = None
CONTROLLER_IP = None


def announce_zeroconf(ip, service_type, service_name='JumpingSumo-SumoProxy'):
    """ Announce the proxied Jumping Sumo.
    """
    zconf = zeroconf.Zeroconf()

    info = zeroconf.ServiceInfo(
        service_type,
        '.'.join((service_name, service_type)),
        socket.inet_aton(ip),
        BOT_INIT_PORT,
        properties={},
    )

    zconf.register_service(info)


class InitHandler(SocketServer.BaseRequestHandler):
    """ SocketServer handler for init handshake.
    """
    def handle(self):
        global BOT_C2DPORT
        global BOT_D2CPORT
        global CONTROLLER_IP

        data = self.request.recv(RECV_MAX)
        print '>', repr(data)

        BOT_D2CPORT = json.loads(data[:-1])['d2c_port']
        CONTROLLER_IP = self.client_address[0]

        bot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bot_socket.connect((BOT_IP, BOT_INIT_PORT))
        bot_socket.sendall(data)
        data = bot_socket.recv(RECV_MAX)
        print '<', repr(data)

        BOT_C2DPORT = json.loads(data[:-1])['c2d_port']

        self.request.sendall(data)
        bot_socket.close()


class C2D_UDPHandler(SocketServer.BaseRequestHandler):
    """ SocketServer handler for data to bot from controller.
    """
    def handle(self):
        data = self.request[0].strip()
        print '>', repr(data)

        bot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bot_socket.sendto(data, (BOT_IP, BOT_C2DPORT))


class D2C_UDPHandler(SocketServer.BaseRequestHandler):
    """ SocketServer handler for data to controller from bot.
    """
    def handle(self):
        data = self.request[0].strip()
        print '<', repr(data)

        controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        controller_socket.sendto(data, (CONTROLLER_IP, BOT_D2CPORT))


if __name__ == '__main__':

    # Announce proxy via Bonjour
    announce_zeroconf(
        PROXY_IP,
        SERVICE_NAME,
    )

    # Create init-handshake server and wait on connection
    init_server = SocketServer.TCPServer(('', BOT_INIT_PORT), InitHandler)
    threading.Thread(target=init_server.serve_forever).start()

    # Wait on getting a port info
    while CONTROLLER_IP is None or BOT_C2DPORT is None or BOT_D2CPORT is None:
        time.sleep(0.01)

    # Handle data from controller to the bot
    c2d_udp_server = SocketServer.UDPServer(('', BOT_C2DPORT), C2D_UDPHandler)
    threading.Thread(target=c2d_udp_server.serve_forever).start()

    # Handle data back from the bot to the controller
    d2c_udp_server = SocketServer.UDPServer(('', BOT_D2CPORT), D2C_UDPHandler)
    d2c_udp_server.serve_forever()

    raw_input('Press Enter to stop...')
