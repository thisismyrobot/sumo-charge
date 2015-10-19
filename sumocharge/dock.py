""" Simple docking example.
"""
import sumopy
import time
import targets


def attempt(conn=None):
    """ Attempt to dock by tracking in on a barcode.
    """
    if conn is None:
        conn = sumopy.SumoController()

    while True:

        # Capture a pic
        pic = conn.get_pic()

        # Get the barcode(s)
        try:
            x_position = [x
                          for (code, (x, _), _)
                          in targets.locate(pic)
                          if code == '0'][0]
        except IndexError:
            time.sleep(0.1)
            continue

        # Default to forwards
        turn = 0

        # Pseudo-proportional control, with deadband
        if abs(x_position) > 5:
            turn = min(10, max(-10, x_position / 5))

        conn.move(10, turn, 0.2)


if __name__ == '__main__':
    attempt()
