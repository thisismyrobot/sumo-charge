""" Simple docking example.
"""
import sumocharge.sumopy
import sumocharge.zbar_decode
import telnetlib


# Close the main process
tconn = telnetlib.Telnet('192.168.2.1', timeout=1)
tconn.read_until('[JS] $ ')
tconn.write('pkill `pidof dragon-prog`\r\n')


conn = sumocharge.sumopy.SumoController()

while True:

    # Capture a pic, as a starting point.
    start_pic = conn.get_pic()
    start_info = [sumocharge.zbar_decode.xy(location, *size)[0]
                  for (code, size, location)
                  in sumocharge.zbar_decode.codes(start_pic)
                  if code == '0']

    # Default to forwards
    left, right = 50, 50

    if len(start_info) == 1:
        # If on left
        if abs(start_info[0]) < 5:
            left, right = 50, 0
        elif start_info[0] > 5:
            left, right = 0, 50

    # Drive, turning right a small amount
    tconn = telnetlib.Telnet('192.168.2.1', timeout=1)
    tconn.read_until('[JS] $ ')
    tconn.write(
        'js_motors -r {} -l {}; usleep 50000; js_motors -r 0 -l 0\r\n'.format(
            -right, -left
        )
    )
    tconn.read_until('[JS] $ ')
