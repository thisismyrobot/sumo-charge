""" Returns "close" Sumos.

    Has to be ran as sudo or iwlist (behind wifi module) doesn't update.
"""
import wifi


def quality(qual_string):
    return int(qual_string.split('/')[0])


def sumos(close_strength=-1):
    """ Return all sumo ssids, sorted by proximity.

        Set close_strength to be => 0 and <= 100 to filter. 100 is perfect
        signal (so closest).
    """
    return [cell.ssid
            for cell
            in sorted(wifi.Cell.all('wlan0'), key=lambda cell: quality(cell.quality), reverse=True)
            if cell.ssid.startswith('JumpingSumo-')
            and quality(cell.quality) > close_strength]


if __name__ == '__main__':
    print sumos(90)
