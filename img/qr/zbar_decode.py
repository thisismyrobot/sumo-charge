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
    raw = pil.tostring()

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
    x_px = sum(map(operator.itemgetter(0), zbar_loc)) / 4.0
    y_px = sum(map(operator.itemgetter(1), zbar_loc)) / 4.0

    # Locate that centre based on 0,0 being the centre of the image
    x_coord = (x_px - (width / 2))
    y_coord = (y_px - (height / 2))

    # Determine what percentage the coordinates are from the centre, return.
    x_percent = (x_coord * 100) / (width / 2)
    y_percent = (y_coord * 100) / (height / 2)

    return x_percent, y_percent


if __name__ == '__main__':
    with open(sys.argv[-1], 'rb') as imgf:
        for (code, size, location) in codes(imgf.read()):
            print code, xy(location, *size)
