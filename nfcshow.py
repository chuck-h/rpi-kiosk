#!/usr/bin/env python3
# NFC interactor
# Raspberry Pi Zero W + PiTFT 240x240

#for display
import board
from digitalio import DigitalInOut
import qrcode

# for NATS
import os
import asyncio
import nats
from nats.errors import TimeoutError

servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")


# set up tft display
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = None
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000
# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

# Load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Turn on the backlight
backlight = DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

async def main():
    # Create the connection to NATS which takes a list of servers.
    nc = await nats.connect(servers=servers)
    sub = await nc.subscribe("local.*")
    print("NATS listening")
    countout = 10
    while True:
        # clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        try:
            msg = await sub.next_msg(timeout=0.1)
            if msg.subject == "local.nfcread": 
              x = 0
              y = top
              HDR = "FOUND TAG"
              draw.text((x, y), HDR, font=font, fill="#FFFFFF")
              y += font.getbbox(HDR)[3]
              UID = f"{msg.data}"
              draw.text((x, y), UID, font=font, fill="#FFFF00")
              y += font.getbbox(UID)[3]
              y += 3
              qr_height = bottom - y
              qr_shift = int((width - qr_height)/2)

              # create a QR code
              qr_img = qrcode.make("NFC "+UID).resize((qr_height,qr_height))
              #combine
              image.paste(qr_img.convert("RGB"),box=(qr_shift, y))
              countout = 10
            elif msg.subject == "local.buy":
              x = 20
              y = top+20
              md = msg.data.decode('UTF-8')
              print (md)
              L1 = md.split('\n')[0]
              draw.text((x, y), L1, font=font, fill="#FFFFFF")
              y += font.getbbox(L1)[3]
              L2 = md.split('\n')[1]
              draw.text((x, y), L2, font=font, fill="#FFFFFF")
              y += 2*font.getbbox(L2)[3]
              L3 = "TAP WRISTBAND"
              draw.text((x, y), L3, font=font, fill="#FFFFFF")
              y += font.getbbox(L3)[3]
              L4 = "   TO BUY"
              draw.text((x, y), L4, font=font, fill="#FFFFFF")
              countout = 150
            # Display image.
            disp.image(image, rotation)
        except TimeoutError:
            countout -= 1
            if countout <= 0:
                disp.image(image, rotation)
                countout = 10
            pass


if __name__ == '__main__':
    asyncio.run(main())

