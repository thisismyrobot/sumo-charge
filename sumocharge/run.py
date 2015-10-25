""" Robot docking management system.
"""
import multiprocessing
import operator
import time


def p_sumo_proxy():
    """ Fire up the proxy - this will spit UDP packets at 127.0.0.1:65432.
    """
    import sumoproxy.proxy
    sumoproxy.proxy.proc_wrapper()


def p_www():
    """ Fire up the web viewer/controller.

        Sits on 0.0.0.0:8000
    """
    import www
    www.launch()


def p_controller():
    """ Fire up the local controller.

        Listens on 127.0.0.1:8001 for UDP packets.
    """
    import local_control
    local_control.main()


def main():
    """ Run all the things.
    """
    targets = (
        p_sumo_proxy,
        p_www,
        p_controller,
    )

    # Create the procs
    procs = [multiprocessing.Process(target=target)
             for target
             in targets]

    # Start them
    map(operator.methodcaller('start'), procs)

    # If any are dead, start them
    while True:
        for i, proc in enumerate(procs):
            if not proc.is_alive():
                proc.terminate()
                procs[i] = multiprocessing.Process(target=targets[i])
                procs[i].start()
            time.sleep(0.1)


if __name__ == '__main__':
    main()
