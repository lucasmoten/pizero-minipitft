# -*- coding: utf-8 -*-

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import requests

#####################################################################################################
# You can disable panels that you don't want to display, or cannot support
enablePanelRunTheNumbers = False
enablePanelRollerCoasterGuy = True
enablePanelMempoolBlocks = True
enablePanelSatsPerFiatUnit = True
# Toggle for whether panels should auto scan to the next panel
autopanel = True
# URLs for endpoints to get data needed for driving display
mempoolurl = "https://mempool.space/api/v1/fees/mempool-blocks"
mempoolblockheighturl = "https://mempool.space/api/blocks/tip/height"
numbersurl = "http://your.own.node:1839/the_numbers_latest.txt"
priceurl = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
#####################################################################################################

panelDiagnostic = 0         # to enable at runtime, press buttons in order: top-bottom-top-bottom-top
panelRunTheNumbers = 1
panelRollerCoasterGuy = 2
panelMempoolBlocks = 3
panelSatsPerFiatUnit = 4

# Start timer to have a basis for elapsed time
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
# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Panels
minPanel = 1 # diagnostic panel is panel 0. This starts with diagnostics disabled
maxPanel = 5
currentPanel = 2
panelDir = 1
drawnPanel = 0
dtPanel = time.time() - start
targetFPS = 5           # realistically due to rendering speed wont get much higher than 5 fps
secondsPerPanel = 10

# Colors
colorbitcoinorange = "#F7931A"
colorbitcoingrey = "#4D4D4D"
colorblack = "#000000"
colorwhite = "#FFFFFF"
colordarkgrey = "#131313"
colormediumgrey = "#353535"
coloryellow = "#FFFF00"
colorgreen = "#00FF00"
colorblue = "#0000FF"
colorpurple = "#FF00FF"
colorred = "#FF0000"
colormempooltext = "#1BD8F4"
# used for mempool block colors based on median fee
colorfee10 = "#039BE5" # blue
colorfee20 = "#11960F" # green
colorfee50 = "#FDD835" # yellow
colorfee100 = "#905206" # orange
colorfee200 = "#B71C1C" # red
colorfee300 = "#3C11C1" # purple
# gradient array for sats per fiat unit display
satscolors = [
    "#FF0000","#FF3F00","#FF7F00","#FFBF00","#FFFF00","#7FFF00","#00FF00","#00FF7F",
    "#FF3F00","#FF7F00","#FFBF00","#FFFF00","#7FFF00","#00FF00","#00FF7F","#00FFFF",
    "#FF7F00","#FFBF00","#FFFF00","#7FFF00","#00FF00","#00FF7F","#00FFFF","#007FFF",
    "#FFBF00","#FFFF00","#7FFF00","#00FF00","#00FF7F","#00FFFF","#007FFF","#0000FF"
]

# Images for rollercoaster guy
imageRCDown     = (Image.open('images/rollercoasterguy-135x240-down.bmp')).convert(mode="RGB")
imageRCFlat     = (Image.open('images/rollercoasterguy-135x240-flat.bmp')).convert(mode="RGB")
imageRCFly      = (Image.open('images/rollercoasterguy-135x240-fly.bmp')).convert(mode="RGB")
imageRCTopLeft  = (Image.open('images/rollercoasterguy-135x240-topleft.bmp')).convert(mode="RGB")
imageRCTopRight = (Image.open('images/rollercoasterguy-135x240-topright.bmp')).convert(mode="RGB")
imageRCUp       = (Image.open('images/rollercoasterguy-135x240-up.bmp')).convert(mode="RGB")

# Bitcoin logo
imageBTC = (Image.open('images/bitcoinlogo-100x100.bmp')).convert(mode="RGB")

# Load in some fonts
fontST = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
fontST2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
fontBTC = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf", 72, encoding="unic")
fontBTC2 = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf", 24, encoding="unic")

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
mempooldata = ""
dtMPB = time.time() - start
if enablePanelMempoolBlocks:
    mempooldata = requests.get(mempoolurl)

# Initial numbers
numbersdata = ""
dtNUM = time.time() - start
if enablePanelRunTheNumbers:
    numbersdata = requests.get(numbersurl)

# Initial price
pricedata = ""
dtPRC = time.time() - start
if enablePanelRollerCoasterGuy or enablePanelSatsPerFiatUnit:
    pricedata = requests.get(priceurl)
    currentprice = pricedata.json()['bitcoin']['usd']
    pricemode = 0

# count for metrics and debounce control
counter = 0
buttonWait = 0
loopstart = time.time()
buttonsPressed = ""

# Functions ------------------------------------------------------------------------------------------------------


def blackscreen():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

def check_for_new_price():
    global dtPRC
    global currentprice
    global pricemode
    if elapsed > (dtPRC + 300): # 5 minutes
        try:
            pricedata = requests.get(priceurl)
            dtPRC = elapsed
        except:
            # fake advance our time so we try again later
            dtPRC = dtPRC + 120
        newprice = pricedata.json()['bitcoin']['usd']
        pricediff = newprice - currentprice
        if pricediff > -5 and pricediff < 5:
            pricemode = 0
        elif pricediff >  5 and pricediff < 100:
            pricemode = 1
        elif pricediff > 100:
            pricemode = 2
        elif pricediff < -5 and pricediff > -100:
            pricemode = -1
        elif pricediff < -100:
            pricemode = -2
        currentprice = newprice

def satssquare(dc, dr, sats, satscolor):
    satsleft = sats
    for y in range(10):
        for x in range(10):
            if satsleft > 0:
                # draw
                tlx = (dc*30)+(x*3)
                tly = (dr*30)+(y*3)
                brx = tlx+1
                bry = tly+1
                draw.rectangle(((tlx,tly),(brx,bry)),satscolor,satscolor)
             # decrement
            satsleft = satsleft - 1

def drawmempoolblock(x, y, medianFee, feeRangeMin, feeRangeMax, nTx, blockLabel):
    blockcolor = colorblack
    textcolor = colorwhite
    if medianFee < 10:
        blockcolor = colorfee10   # blue
    elif medianFee < 20:
        blockcolor = colorfee20   # green
    elif medianFee < 50:
        blockcolor = colorfee50   # yellow
        textcolor = colorblack
    elif medianFee < 100:
        blockcolor = colorfee100  # orange
    elif medianFee < 200:
        blockcolor = colorfee200  # red
    elif medianFee < 300:
        blockcolor = colorfee300  # purple
    else:
        blockcolor = colorblack
    by = 12
    draw.polygon(((x,y+by),(x+103,y+by),(x+118,y+by+15),(x+15,y+by+15)), fill=colormediumgrey, outline=colormediumgrey)
    draw.polygon(((x,y+by),(x+15,y+by+15),(x+15,y+by+118),(x,y+by+103)), fill=colordarkgrey, outline=colordarkgrey)
    draw.polygon(((x+15,y+by+15),(x+118,y+by+15),(x+118,y+by+118),(x+15,y+by+118)), fill=blockcolor, outline=blockcolor)
    t = blockLabel
    w,h = draw.textsize(t, fontST2)
    ox,oy = fontST2.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+0), t, font=fontST2, fill=colormempooltext)
    t = "~%s sat/vB" % (str(medianFee)) # "~350 sat/vB"
    w,h = draw.textsize(t, fontST2)
    ox,oy = fontST2.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+by+20), t, font=fontST2, fill=textcolor)
    t = "%s-%s sat/vB" % (str(feeRangeMin), str(feeRangeMax)) # "100-900 sat/vB"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+by+45), t, font=fontST, fill=textcolor)
    t = "%s" % (str(nTx)) # "2,480"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+by+85), t, font=fontST, fill=textcolor)
    t = "transactions"
    w,h = draw.textsize(t, fontST)
    ox,oy = fontST.getoffset(t)
    w += ox
    h += oy
    draw.text((x+15+(103/2)-(w/2), y+by+95), t, font=fontST, fill=textcolor)

def looppanels():
    global currentPanel
    # loop around bounds
    if currentPanel < minPanel:
        currentPanel = maxPanel - 1
    if currentPanel >= maxPanel:
        currentPanel = minPanel

def is_current_panel_enabled():
    if (not enablePanelMempoolBlocks and currentPanel == panelMempoolBlocks):
        return False
    if (not enablePanelRunTheNumbers and currentPanel == panelRunTheNumbers):
        return False
    if (not enablePanelRollerCoasterGuy and currentPanel == panelRollerCoasterGuy):
        return False
    if (not enablePanelSatsPerFiatUnit and currentPanel == panelSatsPerFiatUnit):
        return False
    return True

def getuserinputs():
    global panelDir
    global currentPanel
    global buttonWait
    global buttonsPressed
    global autopanel
    global minPanel
    global maxPanel
    # User inputs
    if elapsed > buttonWait:
        # just button A (top) pressed
        if buttonA.value and not buttonB.value:
            panelDir = -1
            currentPanel = currentPanel + panelDir
            buttonWait = elapsed + .4
            buttonsPressed = buttonsPressed + "A"
            autopanel = False
        # just button B (bottom) pressed
        if buttonB.value and not buttonA.value:
            panelDir = 1
            currentPanel = currentPanel + panelDir
            buttonWait = elapsed + .4
            buttonsPressed = buttonsPressed + "B"
            autopanel = False
        # both buttons put in auto scan mode
        if not buttonA.value and not buttonB.value:
            panelDir = 1
            autopanel = True
            buttonWait = elapsed + .4
        if buttonsPressed[-5:] == "ABABA":
            # enable diagnostic panel
            minPanel = panelDiagnostic
            buttonsPressed = ""
    # advance panel approx every 10 seconds if auto scan mode 
    if autopanel and (counter % (targetFPS * secondsPerPanel) == 0):
        currentPanel = currentPanel + panelDir
    looppanels()
    # adjust based on panels enabled 
    panelTests = maxPanel
    while ((not is_current_panel_enabled()) and (panelTests > 0)):
        currentPanel = currentPanel + panelDir
        panelTests = panelTests - 1
        looppanels()
    if panelTests == 0:
        autopanel = False
        currentPanel = panelDiagnostic
        minPanel = panelDiagnostic
        maxPanel = panelDiagnostic + 1
        renderPanelDiagnostic()
        exit()

def renderPanelDiagnostic():
    global drawnPanel
    global CPU
    global dtCPU
    global MemUsage
    global dtMEM
    global Disk
    global dtDSK
    global Temp
    global dtTMP
    global elapsed
    global maxPanel
    global panelDiagnostic
    drawnPanel = panelDiagnostic
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
    if maxPanel == panelDiagnostic + 1:
        draw.text((x, y), "NO PANELS ENABLED", font=fontST, fill=colorred)
        y += fontST.getsize("0")[1]
    draw.text((x, y), IP, font=fontST, fill=colorwhite)
    y += fontST.getsize(IP)[1]
    draw.text((x, y), CPU, font=fontST, fill=coloryellow)
    y += fontST.getsize(CPU)[1]
    draw.text((x, y), MemUsage, font=fontST, fill=colorgreen)
    y += fontST.getsize(MemUsage)[1]
    draw.text((x, y), Disk, font=fontST, fill=colorblue)
    y += fontST.getsize(Disk)[1]
    draw.text((x, y), Temp, font=fontST, fill=colorpurple)
    y += fontST.getsize(Temp)[1]
    # Counter, FPS, and Sleep Target aiming for 5 FPS is updated every cycle
    y += 10
    draw.text((x, y), "Counter:" + str(counter), font=fontST, fill=colorbitcoinorange)
    y += fontST.getsize("0")[1]
    fps = counter / elapsed
    draw.text((x, y), "FPS: " + str(fps), font=fontST, fill=colorbitcoinorange)
    y += fontST.getsize("0")[1]
    elapsed = time.time() - loopstart
    st = (counter * (1 / targetFPS)) - elapsed
    draw.text((x, y), "Sleep Target: " + str(st), font=fontST, fill=colorbitcoinorange)
    disp.image(image, rotation)

def renderPanelRunTheNumbers():
    global drawnPanel
    global dtPanel
    global numbersdata
    global dtNUM
    drawnPanel = panelRunTheNumbers
    dtPanel = elapsed
    # Update data if enough time has past
    if elapsed > (dtNUM + 300): # 5 minutes
        try:
            numbersdata = requests.get(numbersurl)
            dtNUM = time.time() - start
        except:
            dtNUM = dtNUM + 60
    blackscreen()
    image.paste(imageBTC,(0,0,100,100))
    xo = 105
    yo = 13
    draw.rectangle((0 + xo, 0, width - xo, height), outline=0, fill=0)
    numbersjson = numbersdata.json()
    lastrunblock = numbersjson['height']
    totalsupply = numbersjson['total_amount']
    draw.text((xo,yo), "Block Height", font=fontST, fill=colorwhite)
    draw.text((xo,yo+17), str(lastrunblock), font=fontST, fill=colorbitcoinorange)
    draw.text((xo,yo+50), "Total Supply", font=fontST, fill=colorwhite)
    draw.text((xo,yo+67), str(totalsupply), font=fontST, fill=colorbitcoinorange)
    draw.text((15,xo), "Run The Numbers!", font=fontBTC2, fill=colorbitcoinorange)
    disp.image(image, rotation)

def renderPanelRollerCoasterGuy():
    global drawnPanel
    global dtPanel
    global dtPRC
    global currentprice
    global pricemode
    drawnPanel = panelRollerCoasterGuy
    dtPanel = elapsed
    blackscreen()
    check_for_new_price()
    rcg = Image.new("RGB", (width, height))
    rcgdraw = ImageDraw.Draw(rcg)
    if pricemode == -2:
        rcg.paste(imageRCDown, (0,0))
        rcgdraw.text((122,17),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((119,14),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((120,15),"$" +  str(currentprice), font=fontBTC2, fill=colorbitcoinorange)
    if pricemode == -1:
        rcg.paste(imageRCTopRight, (0,0))
        rcgdraw.text((12,7),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((9,4),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((10,5),"$" +  str(currentprice), font=fontBTC2, fill=colorbitcoinorange)
    if pricemode == 0:
        rcg.paste(imageRCFlat, (0,0))
        rcgdraw.text((12,107),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((9,104),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((10,105),"$" +  str(currentprice), font=fontBTC2, fill=colorbitcoinorange)
    if pricemode == 1:
        rcg.paste(imageRCTopLeft, (0,0))
        rcgdraw.text((122,7),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((119,4),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((120,5),"$" +  str(currentprice), font=fontBTC2, fill=colorbitcoinorange)
    if pricemode == 2:
        rcg.paste(imageRCUp, (0,0))
        rcgdraw.text((12,17),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((9,14),"$" +  str(currentprice), font=fontBTC2, fill=colorblack)
        rcgdraw.text((10,15),"$" +  str(currentprice), font=fontBTC2, fill=colorbitcoinorange)
    disp.image(rcg, rotation)

def renderPanelMempoolBlocks():
    global drawnPanel
    global dtPanel
    global dtMPB
    global mempoolblockheight
    drawnPanel = panelMempoolBlocks
    dtPanel = elapsed
    # Update data if enough time has past
    newmempooldata = mempooldata
    if elapsed > (dtMPB + 120): # 2 minutes
        try:
            newmempooldata = requests.get(mempoolurl)
            dtMPB = elapsed
        except:
            # fake advance the last mempool time by a minute to delay next check
            dtMPB = dtMPB + 60
    blackscreen()
    if mempooldata.status_code == 200:
        mempooljson = newmempooldata.json()
    else:
        mempooljson = mempooldata.json()
    try:
        # Left block
        pendingblock = 1
        medianFee = int(round(mempooljson[pendingblock]['medianFee']))
        feeRangeMin = int(round(mempooljson[pendingblock]['feeRange'][0]))
        feeRangeMax = int(round(list(reversed(list(mempooljson[pendingblock]['feeRange'])))[0]))
        nTx = int(mempooljson[pendingblock]['nTx'])
        drawmempoolblock(0, 0, medianFee, feeRangeMin, feeRangeMax, nTx, "~ 20 Minutes")
        # Right block
        pendingblock = 0
        medianFee = int(round(mempooljson[pendingblock]['medianFee']))
        feeRangeMin = int(round(mempooljson[pendingblock]['feeRange'][0]))
        feeRangeMax = int(round(list(reversed(list(mempooljson[pendingblock]['feeRange'])))[0]))
        nTx = int(mempooljson[pendingblock]['nTx'])
        drawmempoolblock(120, 0, medianFee, feeRangeMin, feeRangeMax, nTx, "~ 10 Minutes")
    except:
        drawmempoolblock(0, 0, 666, 1, 999, 9999)
        drawmempoolblock(120, 0, 999, 999, 999, 9999)
    disp.image(image, rotation)

def renderPanelSatsPerFiatUnit():
    global drawnPanel
    global dtPanel
    drawnPanel = panelSatsPerFiatUnit
    dtPanel = elapsed
    blackscreen()
    check_for_new_price()
    fiatunit = 1.00
    satsperfiatunit = int(round(100000000.0 / (currentprice / fiatunit))) 
    # be as small as need to be to fit within space of 8x4 matrix of 100 per
    while satsperfiatunit > 3200:
        fiatunit = fiatunit / 2
        satsperfiatunit = int(round(100000000.0 / (currentprice / fiatunit))) 
    t = str(satsperfiatunit) + " sats/$" + str(fiatunit)
    dc = 0
    dr = 0
    colorindex = 0
    while satsperfiatunit > 100:
        # decrement satsperfiatunit
        satsperfiatunit = satsperfiatunit - 100
        # draw satssquare
        satssquare(dc, dr, 100, satscolors[colorindex])
        # advance to next square position
        dc = dc + 1
        if dc >= 8:
            dr = dr + 1
            dc = 0
        colorindex = colorindex + 1
    # remainder
    satssquare(dc, dr, satsperfiatunit, satscolors[colorindex])
    # label
    w,h = draw.textsize(t, fontST2)
    ox,oy = fontST2.getoffset(t)
    draw.text((width-w,height-h),t,font=fontST2, fill=colorbitcoinorange)
    disp.image(image, rotation)


# Main routine ---------------------------------------------------------------------------------------------------
while True:
    counter = counter + 1
    elapsed = time.time() - loopstart

    getuserinputs()

    if currentPanel == panelDiagnostic:
        renderPanelDiagnostic()
    if currentPanel == panelRunTheNumbers and ((drawnPanel != panelRunTheNumbers) or (elapsed > dtPanel + 20)):
        renderPanelRunTheNumbers()
    if currentPanel == panelRollerCoasterGuy and ((drawnPanel != panelRollerCoasterGuy) or (elapsed > dtPanel + 20)):
        renderPanelRollerCoasterGuy()
    if currentPanel == panelMempoolBlocks and ((drawnPanel != panelMempoolBlocks) or (elapsed > dtPanel + 20)):
        renderPanelMempoolBlocks()
    if currentPanel == panelSatsPerFiatUnit and ((drawnPanel != panelSatsPerFiatUnit) or (elapsed > dtPanel + 20)):
        renderPanelSatsPerFiatUnit()

    elapsed = time.time() - loopstart
    st = (counter * (1 / targetFPS)) - elapsed
    if st > 0:
        time.sleep(st)