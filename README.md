# Sumo Charge

An attempt to do wireless charging of a Parrot Jumping Sumo using a Raspberry
Pi and some bits and bobs. This will hopefully allow for hands-free docking.

![System design](/img/system.png?raw=true)

## Installation

From within the cloned repository (assuming on Rasbian):

    git submodule init
    git submodule update

    virtualenv venv
    venv/bin/pip install -r requirements.txt
    venv/bin/pip install -r sumocharge/sumoproxy/requirements.txt

    sudo apt-get install python-qrtools

## Usage

Eventually...:

    venv/bin/python sumocharge/run.py

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

## Hat tips

 * Heaps of pointers toward the byte format for commands: https://github.com/haraisao/JumpingSumo-Python

## For when I forget

Updating the submodules to most recent commit:

    git submodule foreach git pull origin master
