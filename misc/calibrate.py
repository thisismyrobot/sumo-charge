""" QR code control data gatherer.

    Every time <ENTER> is pressed a pic is taken. Then the angle to, and size
    of, any QR codes in the pic is recorded.

    Then a 0.1 second motor pulse is ran towards centering the pic.

    Then the angle to is taken again, from a fresh pic.
"""
import get_frame
import operator
import re
import telnetlib
import time
import zbar_decode


QRMAP = {
    u'\u7b18\uff79': 'big',
    u'\u7b18\uff7a': 'small',
}

# Close the main process
tconn = telnetlib.Telnet('192.168.2.1', timeout=1)
tconn.read_until('[JS] $ ')
tconn.write('pkill `pidof dragon-prog`\r\n')


while True:

    # Capture a pic, as a starting point.
    start_pic = get_frame.snapshot_ftp()
    start_info = [(code,
                   zbar_decode.xy(location, *size)[0],
                   zbar_decode.width(location))
                  for (code, size, location)
                  in zbar_decode.codes(start_pic)]

    if len(start_info) == 0:
        print 'No QR!'
        break

    # Deterministically order QR codes by size.
    start_info.sort(key=operator.itemgetter(2))

    # Drive, turning right a small amount
    tconn = telnetlib.Telnet('192.168.2.1', timeout=1)
    tconn.read_until('[JS] $ ')
    tconn.write(
        'time js_motors -r -50 -l 50 > /dev/null; js_motors -r 0 -l 0 > /dev/null\r\n'
    )
    data = tconn.read_until('[JS] $ ')

    # Capture how long we drove for, usually something like 0.02 (seconds).
    duration = float(re.search('real    0m (.*?)s', data).groups()[0])

    # Capture a new pic
    end_pic = get_frame.snapshot_ftp()
    end_info = [(code,
                 zbar_decode.xy(location, *size)[0],
                 zbar_decode.width(location))
                for (code, size, location)
                in zbar_decode.codes(end_pic)]

    if len(start_info) != len(end_info):
        print 'Change in count of QRs!'
        break

    # Deterministically order QR codes by size.
    end_info.sort(key=operator.itemgetter(2))

    for i in range(len(start_info)):
        qr_code = QRMAP[start_info[i][0]]
        start_width = start_info[i][2]

        # Where we start moving is important due to camera distortion.
        start_x = abs(start_info[i][1])

        # We need to know how far (%) we moved per second of time.
        movement_ratio = abs(start_info[i][1] - end_info[i][1]) / duration

        print ','.join(map(str, (
            qr_code, start_width, start_x, movement_ratio
        )))
