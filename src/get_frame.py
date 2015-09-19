""" Parrot Jumping Sumo frame grabber.
"""
import base64
import ftplib
import socket
import telnetlib
import threading
import SocketServer
import StringIO


PARROT_IP = '192.168.2.1'


def snapshot_ftp(ip_addr=PARROT_IP, timeout=1):
    """ Returns raw JPEG data from Parrot jumping sumo, via telnet and FTP.
    """
    # Connect to the sumo and request the image
    try:
        tconn = telnetlib.Telnet(ip_addr, timeout=timeout)
        tconn.read_until('[JS] $ ')
        cmd = '; '.join((
            'kill `pidof dragon-prog` 2> /dev/null',
            'mkdir -p /data/ftp/ram',
            'umount /data/ftp/ram',
            'mount -t tmpfs -o size=1m tmpfs /data/ftp/ram',
            'yavta --skip=1 -c2 -n1 -F/data/ftp/ram/snap.jpg /dev/video0 > /dev/null'
        )) + '\r\n'
        tconn.write(cmd)
    except socket.timeout:
        raise Exception('Failed to connect to Jumping Sumo and request image.')

    tconn.read_until('[JS] $ ')

    ftp = ftplib.FTP(ip_addr)
    ftp.login()
    ftp.cwd('ram')
    strf = StringIO.StringIO()
    ftp.retrbinary('RETR snap.jpg', strf.write)
    return strf.getvalue()


def snapshot_socket(ip_addr=PARROT_IP, listen_port=49999, timeout=1):
    """ Returns raw JPEG data from Parrot jumping sumo, via telnet and
        sockets.
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
                def tidy():
                    server.shutdown()
                    server.server_close()
                threading.Thread(target=tidy).start()

    # Start a server in a thread with that handler
    server = SocketServer.TCPServer(('', listen_port), Handler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Connect to the sumo and request the image
    try:
        tconn = telnetlib.Telnet(ip_addr, timeout=timeout)
        tconn.read_until('[JS] $ ')
        cmd = 'yavta --skip=1 -c2 -n1 -S{}:{} /dev/video0\r\n'.format(
            my_ip, listen_port
        )
        tconn.write(cmd)
    except socket.timeout:
        raise Exception('Failed to connect to Jumping Sumo and request image.')

    # Wait on image being received
    server_thread.join(timeout)
    if server_thread.isAlive():
        raise Exception('No image received from Jumping Sumo.')

    return img_data[0]


def snapshot(ip_addr=PARROT_IP, width=160, height=120, timeout=1):
    """ Returns raw JPEG data from Parrot jumping sumo.
    """
    # Connect to the sumo and request the image
    try:
        tconn = telnetlib.Telnet(ip_addr, timeout=timeout)
        tconn.read_until('[JS] $ ')
        tconn.write('kill `pidof dragon-prog`\r\n')
        tconn.read_until('[JS] $ ')
        tconn.write(
            ' '.join((
                'echo \'\' > /dev/stdout',
                ';',
                'yavta',
                '--skip=1',
                '-s{}x{}'.format(width, height),
                '-c2',
                '-F/dev/stdout',
                '-fMJPEG',
                '/dev/video0',
                '> /dev/null',
                ';',
                'base64 /dev/stdout',
            )) + '\r\n'
        )
    except socket.timeout:
        raise Exception('Failed to connect to Jumping Sumo and request image.')

    res = tconn.read_until(
        '[JS] $ '
    ).split('base64 /dev/stdout')[1].replace('\r\n', '')[:-7]

    return base64.b64decode(res)[1:]


if __name__ == '__main__':
    with open('snapshot.jpg', 'wb') as f:
        f.write(snapshot())

    with open('snapshot_ftp.jpg', 'wb') as f:
        f.write(snapshot_ftp())

    with open('snapshot_socket.jpg', 'wb') as f:
        f.write(snapshot_socket())
