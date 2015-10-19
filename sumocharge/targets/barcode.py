""" QR code detector.

    For each detected code it returns the code and the x/y center location
    between +/-100 percent of the image.
"""
import operator
import sys
import zbar
import PIL.Image
import StringIO


def codes(image_data):
    """ Return [(code, location)...] for codes in image.

        Heavily based on:
            https://code.google.com/p/qtqr/source/browse/qrtools.py
    """
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    pil = PIL.Image.open(StringIO.StringIO(image_data)).convert('L')
    width, height = pil.size
    raw = pil.tobytes()

    image = zbar.Image(width, height, 'Y800', raw)

    scanner.scan(image)

    return [(s.data.decode(u'utf-8'), image.size, s.location)
            for s
            in image]


def xy(zbar_loc, width, height):
    """ Converts zbar location to percent (+/-100) position from center.

        Image center in top-left would be -100, -100. Image center in bottom
        left would be -100, 100. Etc Etc.

    """
    # Locate the centre of the QR code
    x_px = sum(map(operator.itemgetter(0), zbar_loc)) / len(zbar_loc)
    y_px = sum(map(operator.itemgetter(1), zbar_loc)) / len(zbar_loc)

    # Locate that centre based on 0,0 being the centre of the image
    x_coord = (x_px - (width / 2))
    y_coord = (y_px - (height / 2))

    # Determine what percentage the coordinates are from the centre, return.
    x_percent = (x_coord * 100) / (width / 2)
    y_percent = (y_coord * 100) / (height / 2)

    return x_percent, y_percent


def get_width(zbar_loc):
    """ Returns width of QR code.
    """
    left_side  = (zbar_loc[0][0] + zbar_loc[1][0]) / 2
    right_side = (zbar_loc[2][0] + zbar_loc[3][0]) / 2
    return right_side - left_side


def locate(image):
    """ Returns code, x, y and width of detected targets in image.
    """
    return [(code, xy(location, *size), get_width(location))
            for (code, size, location)
            in codes(image)]

if __name__ == '__main__':
    with open(sys.argv[-1], 'rb') as imgf:
        for result in locate(imgf.read()):
            print result
