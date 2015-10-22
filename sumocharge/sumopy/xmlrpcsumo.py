import interface
import sys
import time
import xmlrpclib
import SimpleXMLRPCServer


def start_server(funcs, host='127.0.0.1', port=8000):
    """ XMLRPC server.

        Pass {'name': func, ...} dict.
    """
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)
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
        return xmlrpclib.Binary(sumo.get_pic())
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

            # Blocking
            print 'Starting server...'
            start_server({
                'move': proxy_move(sumo),
                'pic': proxy_pic(sumo),
            })

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
