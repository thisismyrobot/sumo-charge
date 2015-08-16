import pifacedigitalio


RELAY_ON = False

def switch_pressed(event):
    global RELAY_ON

    if not RELAY_ON:
        event.chip.output_pins[0].turn_on()
        event.chip.output_pins[1].turn_on()
    else:
        event.chip.output_pins[0].turn_off()
        event.chip.output_pins[1].turn_off()

    RELAY_ON = not RELAY_ON


if __name__ == '__main__':

    pifacedigital = pifacedigitalio.PiFaceDigital()

    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    listener.register(0, pifacedigitalio.IODIR_ON, switch_pressed)
    listener.activate()
