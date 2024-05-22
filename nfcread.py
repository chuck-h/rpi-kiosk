#!/usr/bin/env python3
# NFC interactor
# Publish card-read events on "local.nfcread"
# PN532 NFC reader + Raspberry Pi Zero W 

# for NFC reader
import board
from digitalio import DigitalInOut
from adafruit_pn532.uart import PN532_UART
import serial

# for NATS
import os
import asyncio
import nats
from nats.errors import TimeoutError

# set up NATS
servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")

# set up NFC reader
uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.1)
pn532 = PN532_UART(uart, debug=False)
pn532.SAM_configuration()

async def main():
    # Create the connection to NATS which takes a list of servers.
    nc = await nats.connect(servers=servers)
    while True:
        await asyncio.sleep(0) # yield the thread
        uid = pn532.read_passive_target(timeout=0.5)
        #print('.', end="", flush=True)
        if uid is None:
            continue
        print('Found card with UID:', [hex(i) for i in uid])
        UID = '.'.join(map(str,uid))
        await nc.publish("local.nfcread", bytes(UID, "utf-8"))
 
if __name__ == '__main__':
    asyncio.run(main())
