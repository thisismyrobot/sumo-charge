""" Parrot Jumping Sumo frame grabber.
"""
import socket
import telnetlib
import threading
import SocketServer


PARROT_IP = '192.168.2.1'
LISTEN_PORT = 49999


def snapshot(ip_addr, listen_port, width=160, height=120, timeout=1):
    """ Returns raw jpeg data from Parrot jumping sumo.
    """

    # Determine my IP address on the interface connected to the sumo
    try:
        my_ip = [ip
                 for ip
                 in socket.gethostbyname_ex(socket.gethostname())[2]
                 if ip.startswith('.'.join(ip_addr.split('.')[:-1]) + '.')][0]
    except IndexError:
        raise Exception(
            'Cannot determine IP address assigned by Parrot Jumping Sumo.'
        )


    # Build a handler that can shutdown after one request
    img_data = []
    server = None
    class Handler(SocketServer.BaseRequestHandler):
        """ Handler for connections from the server.
        """
        def handle(self):
            try:
                img_data.append(self.request.recv(102400)) # 100KB
            finally:
                threading.Thread(target=server.shutdown).start()

    # Start a server in a thread with that handler
    server = SocketServer.TCPServer(('', listen_port), Handler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Connect to the sumo and request the image
    tconn = telnetlib.Telnet(ip_addr)
    tconn.read_until('[JS] $', 1)
    tconn.write('kill `pidof dragon-prog`2>/dev/null\n')
    tconn.write(
        ' '.join((
            'yavta',
            '--skip=1',
            '-s{}x{}'.format(width, height),
            '-c2',
            '-S{}:{}'.format(my_ip, listen_port),
            '-fMJPEG',
            '/dev/video0',
        )) + '>/dev/null\n'
    )

    # Wait on image being recieved
    server_thread.join(timeout)
    if server_thread.isAlive():
        raise Exception('No image recieved from Jumping Sumo')

    return img_data[0]


if __name__ == '__main__':
    with open('sumo.jpg', 'wb') as f:
        f.write(snapshot(PARROT_IP, LISTEN_PORT))
