# Sumo Charge

An attempt to do wireless charging of a Parrot Jumping Sumo using a Raspberry
Pi and some bits and bobs. This will hopefully allow for hands-free docking.

## Hardware

### Currently

 * [Parrot Jumping Sumo](http://www.parrot.com/au/products/jumping-sumo/)
 * [Raspberry Pi 1 Model B](https://www.raspberrypi.org/products/model-b/)
 * [PiFace Digital](http://www.piface.org.uk/products/piface_digital/)
 * [5V 600mA Wireless Charging Module](http://littlebirdelectronics.com.au/products/wireless-charging-module-1)
 * [13.56MHz RFID Module](http://littlebirdelectronics.com.au/products/13-56mhz-rfid-module-ios-iec-14443-type-a)
 * [13.56MHz RFID Tag](http://littlebirdelectronics.com.au/products/m1-rfid-tag-13-56mhz)
 * [WiPi WiFi dongle](http://raspberry.piaustralia.com.au/collections/wifi/products/wipi-dongle-wifi)

### The future?

 * Camera?

## Software

 * Raspbian on the Pi

 * Python deps:

    pip install -r requirements.txt

 * Python QR tools:

    sudo apt-get install python-qrtools

 * TBD...

## Hat tips

 * Heaps of pointers toward the byte format for commands: https://github.com/haraisao/JumpingSumo-Python
