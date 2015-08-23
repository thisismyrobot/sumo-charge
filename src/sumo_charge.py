""" Charge-starting code for Parrot Jumping Sumo.
"""
import pifacedigitalio
import mifare
import threading
import time
import usb_serial


# Will look at looping back the digital outs to some "ins" to detect this...
CHARGING = False


def start_charging(chip):
    """ Enable the charging relays.
    """
    global CHARGING
    CHARGING = True
    chip.output_pins[0].turn_on()
    chip.output_pins[1].turn_on()


def stop_charging(chip):
    """ Disable the charging relays.
    """
    global CHARGING
    CHARGING = False
    chip.output_pins[0].turn_off()
    chip.output_pins[1].turn_off()


def switch_pressed(event):
    """ Handler for when button 1 is pressed.
    """
    global CHARGING
    if not CHARGING:
        start_charging(event.chip)
    else:
        stop_charging(event.chip)


if __name__ == '__main__':

    # Set up the piface
    pifacedigital = pifacedigitalio.PiFaceDigital()

    # We need a usb serial port - the one with RFID connected would be great.
    io = usb_serial.first()

    # Set up the RFID reader loop
    rfid = mifare.RFID(io)

    def rfid_thread():
        while True:
            # If tag detected and we're not already charging, start charging
            # in 5 seconds.
            if rfid.serial() != [] and not CHARGING:
                time.sleep(5)
                start_charging(pifacedigital)
            time.sleep(1)
    threading.Thread(target=rfid_thread).start()

    # Configure the charging button and event handling
    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    listener.register(0, pifacedigitalio.IODIR_ON, switch_pressed)
    listener.activate()
