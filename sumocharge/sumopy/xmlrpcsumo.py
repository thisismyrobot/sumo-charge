import interface
import sys
import threading
import time
import xmlrpclib
import SimpleXMLRPCServer


def start_server(funcs, host='127.0.0.1', port=8000):
    """ XMLRPC server.

        Pass {'name': func, ...} dict.
    """
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)

    reload(xmlrpclib)

    class ProxyFault(xmlrpclib.Fault):
        """ We want to catch faults on the server too, to restart it.
        """
        def __init__(self, *args, **kwargs):
            super(ProxyFault, self).__init__(*args, **kwargs)
            threading.Thread(target=server.shutdown).start()
    xmlrpclib.Fault = ProxyFault

    for (name, func) in funcs.items():
        server.register_function(func, name)
    server.serve_forever()


def proxy_move(sumo):
    """ Calls the 'move' function in non-blocking mode.
    """
    def non_block_move(speed, turn, duration):
        sumo.move(speed, turn, duration, block=False)
    return non_block_move


def proxy_pic(sumo):
    """ Calls the 'get_pic' function and returns a Binary result.
    """
    def get_pic_binary():
        pic = sumo.get_pic(retries=0)
        if pic is None:
            raise Exception('No connection? (couldn\'t get pic)')
        return xmlrpclib.Binary(pic)
    return get_pic_binary


def main():
    """ XMLRPC server for sumopy.

        Allows multiple clients to manage a single Sumo.

        Attempts to be resilient...
    """
    while True:
        try:

            print 'Creating Sumo...'
            sumo = interface.SumoController()

            # Blocking - exceptions will stop though.
            print 'Starting server...'
            start_server({
                'move': proxy_move(sumo),
                'pic': proxy_pic(sumo),
            })
            raise Exception('SimpleXMLRPCServer detected client error')

        except interface.SumoPyException as spe:

            sys.stderr.write(
                'SumoPyException: {}\n'.format(spe)
            )

        except Exception as e:

            sys.stderr.write(
                'Exception: {}\n'.format(e)
            )

        time.sleep(5)


if __name__ == '__main__':
    main()
