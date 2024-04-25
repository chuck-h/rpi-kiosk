# rpi-kiosk
A kiosk system which initiates blockchain transactions based on NFC tag

Inspired by NFC Wallet March 2024 https://drive.google.com/file/d/1Ph_7cQGZvrkj3zASVVKsac3wuu9phT2F/view

## Status
This project is in a chaotic early protoyping stage. This README is probably already obsolete because software moves faster than documentation!
An early brainstorming document is here: https://docs.google.com/document/d/1bi9Xqc3jPMIKPmWmw_7Wpaw240WUTF4ko1_ypiXqWYI/edit

## Hardware configuration

The prototype is built with a Raspberry Pi Zero W, which uses an Arm6 processor and runs a variant of Debian Linux. https://www.raspberrypi.com/products/raspberry-pi-zero-w/ This board includes Wifi for internet connectivity.

 ![image](https://github.com/chuck-h/rpi-kiosk/assets/2141014/5e289b77-66a3-489c-abc2-cc734429d75a)

The Raspberry Pi devices are designed to attach to a wide variety of peripherals, in our case an NFC reader and display. Big shout-out to Adafruit for peripheral harware and software support. https://www.adafruit.com/

### NFC reader
PN532-based NFC reader peripheral, connected through serial port. https://www.adafruit.com/product/364

### 1.3-inch display
1.3-inch 240x240 color TFT display, connected through SPI. https://www.adafruit.com/product/4484

### Alternative displays
The processor board includes an HDMI port which can connect with larger display screens, and can also support touchscreen input. These features are not being used in the prototype.

## Software architecture
This project uses loosely-coupled coprocessing where independent programs communicate through the nats.io publish/subscribe messaging framework. Separate processes handle NFC reading, display, and blockchain communication.

### Messaging framework
The nats.io messaging framework is designed to handle both local and wide-area-network messaging. In this project we are only using it locally within the kiosk processor. A local server daemon manages this. https://nats.io 

### NFC reader
_nfcread.py_ communicates with the NFC reader peripheral over a serial port. When a tag is present, it publishes a message containing the tag serial number on the `local.nfcread` channel. The message repeats until the tag is removed. If multiple tags are present, the PN532 chip will report them alternately.

### Display
_nfcshow.py_ is connected to the TFT display. It listens on the `local.nfcread` channel and displays the serial number as text at the top of the display. It also computes and displays (as a demo) a QR code representing the serial number.

![image](https://github.com/chuck-h/rpi-kiosk/assets/2141014/70f1f0fe-de19-47a5-8e23-da47a6baedec)

### Blockchain interface (antelope)
_antelope.py_ incorporates wharfkit tools https://wharfkit.com/ to interface with antelope (formerly eosio) blockchains. It listens for nats.io messages and takes actions such as reading a table or publishing a transaction to the public chain over wifi internet.

### Blockchain interface (EVM)
To be written

## Installation

### Operating system
Raspberry Pi OS Lite  Release date: March 15th 2024 based on Debian 12 (Bookworm) https://www.raspberrypi.com/software/operating-systems/

### Messaging framework
Server daemon `sudo apt install nats-server`

Python libraries `pip3 install nats-py`

JS libraries `npm install nats`

### Python peripheral support
Adafruit CircuitPython https://learn.adafruit.com/circuitpython-on-raspberrypi-linux

Adafruit NFC reader https://learn.adafruit.com/adafruit-pn532-rfid-nfc/python-circuitpython

Adafruit TFT display https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup

### Antelope blockchain support
Greymass wharfkit `npm install @wharfkit/session @wharfkit/wallet-plugin-privatekey @wharfkit/contract dotenv`

### Running the application
At this time it is necessary to start each application manually
```
python3 nfcread.py &
python3 nfcshow.py &
node antelope.js
```



