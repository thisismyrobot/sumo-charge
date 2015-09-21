""" QR code detector.

    Heavily based on: https://code.google.com/p/qtqr/source/browse/qrtools.py
"""
import sys
import zbar
import PIL.Image
import StringIO


def codes(image_data):
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    pil = PIL.Image.open(StringIO.StringIO(image_data)).convert('L')
    width, height = pil.size
    raw = pil.tostring()

    image = zbar.Image(width, height, 'Y800', raw)

    scanner.scan(image)

    return [(s.data.decode(u'utf-8'), s.location)
            for s
            in image]


if __name__ == '__main__':
    with open(sys.argv[-1], 'rb') as imgf:
        print codes(imgf.read())
