# -*- coding: utf-8 -*-

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import requests

mempoolapi = "https://mempool.space/api/v1/fees/mempool-blocks"

# Start timer
start = time.time()


# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
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
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Button assignment
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Panels
maxPanel = 4
currentPanel = 3

# Colors
bitcoinorange = "#f7931a"
bitcoingrey = "#4d4d4d"

# Images for rollercoaster guy
imageRCOrig = Image.open('bitcoin-rollercoaster.jpg')
imageRCCrop = imageRCOrig.crop((1,150,874,775))
imageRCSize = imageRCCrop.resize((240,135))
imageRCUp       = (Image.open('rollercoasterguy-135x240-up.bmp')).convert(mode="RGB")
imageRCDown     = (Image.open('rollercoasterguy-135x240-down.bmp')).convert(mode="RGB")
imageRCFly      = (Image.open('rollercoasterguy-135x240-fly.bmp')).convert(mode="RGB")
imageRCTopLeft  = (Image.open('rollercoasterguy-135x240-topleft.bmp')).convert(mode="RGB")
imageRCTopRight = (Image.open('rollercoasterguy-135x240-topright.bmp')).convert(mode="RGB")
imageRCFlat     = (Image.open('rollercoasterguy-135x240-flat.bmp')).convert(mode="RGB")

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding


# Load in some fonts
fontST = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
fontST2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
fontBTC = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf", 96, encoding="unic")
fontMP = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)

# Initial stats
# Shell scripts for system monitoring from here:
# https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
cmd = "hostname -I | cut -d' ' -f1"
IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
dtCPU = time.time() - start
MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
dtMEM = time.time() - start
Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
dtDSK = time.time() - start
Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
dtTMP = time.time() - start

# Initial mempool
mempooldata = requests.get(mempoolapi)
dtMPB = time.time() - start

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Stick to a given frame rate
targetFPS = 5

# count for metrics and debounce control
counter = 0
buttonWait = 0


def drawmempoolblock(x, y, medianFee, feeRangeMin, feeRangeMax, nTx):
    blockcolor = "#905206"
    if medianFee < 20:
        blockcolor = "#11960f" # green
    elif medianFee < 50:
        blockcolor = "#905206" # orange
    elif medianFee < 200:
        blockcolor = "#960f41" # red
    else:
        blockcolor = "#3c11c1" # purple
    draw.polygon(((x,y),(x+103,y),(x+118,y+15),(x+15,y+15)), fill="#353535", outline="#353535")
    draw.polygon(((x,y),(x+15,y+15),(x+15,y+118),(x,y+103)), fill="#131313", outline="#131313")
    draw.polygon(((x+15,y+15),(x+118,y+15),(x+118,y+118),(x+15,y+118)), fill=blockcolor, outline=blockcolor)
    t = "~%s sat/vB" % (str(medianFee)) # "~350 sat/vB"
    w,h = draw.textsize(t, fontST2)
    ox,oy = fontST2.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+20), t, font=fontST2, fill="#FFFFFF")
    t = "%s-%s sat/vB" % (str(feeRangeMin), str(feeRangeMax)) # "100-900 sat/vB"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+45), t, font=fontST, fill="#FFFFFF")
    t = "%s" % (str(nTx)) # "2,480"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+85), t, font=fontST, fill="#FFFFFF")
    t = "transactions"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+95), t, font=fontST, fill="#FFFFFF")


loopstart = time.time()
while True:
    counter = counter + 1
    elapsed = time.time() - start

    # User inputs
    if elapsed > buttonWait:
        # just button A (up) pressed
        if buttonA.value and not buttonB.value:
            panelDir = 1
            currentPanel = currentPanel + panelDir
            buttonWait = elapsed + .4
        # just button B (down) pressed
        if buttonB.value and not buttonA.value:
            panelDir = -1
            currentPanel = currentPanel + panelDir
            buttonWait = elapsed + .4
        # loop around bounds
        if currentPanel < 0:
            currentPanel = maxPanel - 1
        if currentPanel >= maxPanel:
            currentPanel = 0

    # Debug Stats
    if currentPanel == 0:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        # Dont update on every cycle. Too taxing, little change
        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        if elapsed > (dtCPU + 30): # 30 seconds
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
            dtCPU = elapsed
        if elapsed > (dtMEM + 90): # 1.5 minutes
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
            MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
            dtMEM = elapsed
        if elapsed > (dtDSK + 1800): # 30 minutes
            cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
            Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
            dtDSK = elapsed
        if elapsed > (dtTMP + 20): # 20 seconds
            cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
            Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
            dtTMP = elapsed

        # Write out the statistics
        x = 0
        y = top
        draw.text((x, y), IP, font=fontST, fill="#FFFFFF")
        y += fontST.getsize(IP)[1]
        draw.text((x, y), CPU, font=fontST, fill="#FFFF00")
        y += fontST.getsize(CPU)[1]
        draw.text((x, y), MemUsage, font=fontST, fill="#00FF00")
        y += fontST.getsize(MemUsage)[1]
        draw.text((x, y), Disk, font=fontST, fill="#0000FF")
        y += fontST.getsize(Disk)[1]
        draw.text((x, y), Temp, font=fontST, fill="#FF00FF")
        y += fontST.getsize(Temp)[1]
        # Counter, FPS, and Sleep Target aiming for 5 FPS is updated every cycle
        y += 10
        draw.text((x, y), "Counter:" + str(counter), font=fontST, fill=bitcoinorange)
        y += fontST.getsize("0")[1]
        fps = counter / elapsed
        draw.text((x, y), "FPS: " + str(fps), font=fontST, fill=bitcoinorange)
        y += fontST.getsize("0")[1]
        elapsed = time.time() - start
        st = (counter * (1 / targetFPS)) - elapsed
        draw.text((x, y), "Sleep Target: " + str(st), font=fontST, fill=bitcoinorange)
        disp.image(image, rotation)

    # Bitcoin logo
    if currentPanel == 1:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        y = top
        draw.ellipse((10,10,125,125), fill=bitcoinorange, outline=bitcoinorange)
        y = 10
        x = 30
        draw.text((x, y), "B", font=fontBTC, fill="#FFFFFF")
        disp.image(image, rotation)

    # Bitcoin Roller Coaster Guy
    if currentPanel == 2:
        draw.rectangle((0,0,width,height),outline=0,fill=0)
        if counter % 10 < 2:
            disp.image(imageRCFly, rotation)
        elif counter % 10 < 4:
            disp.image(imageRCUp, rotation)
        elif counter % 10 < 6:
            disp.image(imageRCTopLeft, rotation)
        elif counter % 10 < 8:
            disp.image(imageRCTopRight, rotation)
        elif counter % 10 < 10:
            disp.image(imageRCDown, rotation)

    # Mempool
    if currentPanel == 3:
        # Update data if enough time has past
        if elapsed > (dtMPB + 120):
            mempooldata = requests.get(mempoolapi)
            dtMPB = elapsed
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        mempooljson = mempooldata.json()
        # Left block
        pendingblock = 1
        medianFee = int(round(mempooljson[pendingblock]['medianFee']))
        feeRangeMin = int(round(mempooljson[pendingblock]['feeRange'][0]))
        feeRangeMax = int(round(list(reversed(list(mempooljson[pendingblock]['feeRange'])))[0]))
        nTx = int(mempooljson[pendingblock]['nTx'])
        drawmempoolblock(0, 0, medianFee, feeRangeMin, feeRangeMax, nTx)
        # Right block
        pendingblock = 0
        medianFee = int(round(mempooljson[pendingblock]['medianFee']))
        feeRangeMin = int(round(mempooljson[pendingblock]['feeRange'][0]))
        feeRangeMax = int(round(list(reversed(list(mempooljson[pendingblock]['feeRange'])))[0]))
        nTx = int(mempooljson[pendingblock]['nTx'])
        drawmempoolblock(120, 0, medianFee, feeRangeMin, feeRangeMax, nTx)
        disp.image(image, rotation)

    # Sleep to sync framerate to target
    elapsed = time.time() - loopstart
    st = (counter * (1 / targetFPS)) - elapsed
    if st > 0:
        time.sleep(st)
