""" Robot docking management system.
"""
import multiprocessing


def p_sumo_interface():
    """ Fire up the xmlrpc interface to the sumo.
    """
    import sumopy.xmlrpcsumo
    sumopy.xmlrpcsumo.start()


def p_www():
    """ Fire up the web viewer/controller.
    """
    import www
    www.launch()


def main():
    """ Run all the things.
    """
    multiprocessing.Process(target=p_sumo_interface).start()

    multiprocessing.Process(target=p_www).start()


if __name__ == '__main__':
    main()
