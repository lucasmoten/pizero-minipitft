# Prerequisites

Here are the parts used for this project
- [Raspberry Pi Zero W](https://www.adafruit.com/product/3400) $10.00 USD
- [2x20 pin Header](https://www.adafruit.com/product/2822) $0.95 USD
- [Mini PiTFT 135x240 Color TFT](https://www.adafruit.com/product/4393) $14.95 USD
- [MicroUSB power supply](https://www.adafruit.com/product/1995) $7.95 USD

## Initialize the Raspberry Pi

Before using any scripts in this project, you'll need to setup your Raspberry Pi with the basics

1. Acquire necessary components as listed above.  This project uses a Raspberry Pi Zero W, but any Raspberry Pi with networking support and modern header layout should suffice.

2. If using the recommended Raspberry Pi Zero W, solder on the pin header as you normally would, or acquire one with pins presoldered.

3. Install operation system as Raspberry Pi Os Lite using Raspberry Pi Imager.  Follow guidance here: https://www.raspberrypi.org/software/

4. Next you'll want to enable SSH, setup your wifi settings on the Micro SD card.

5. Once powered up, identify the raspberry Pi on the network and SSH in.  The default credentials are pi/raspberry, and you should change these

6. Once logged in, run `sudo raspi-config` and enable the interfaces for SPI and I2C.  Save and exit, reboot the pi and SSH back in after startup


## Install CircuitPython Libraries on Raspberry Pi

This project depends on Python and assorted libraries

Follow instructions here:
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

Which are paraphrased as follows

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y python3 git python3-pip
sudo update-alternatives --install /usr/bin/python python $(which python2) 1
sudo update-alternatives --install /usr/bin/python python $(which python3) 2
sudo update-alternatives --config python
pip3 install RPI.GPIO
pip3 install adafruit-blinka
```

## Install for RGB display

Now run these commands

```bash
sudo pip3 install adafruit-circuitpython-rgb-display
sudo pip3 install --upgrade --force-reinstall spidev
```

## Install fonts

```bash
sudo apt-get install ttf-dejavu
wget https://assets.ubuntu.com/v1/0cef8205-ubuntu-font-family-0.83.zip
unzip 0cef8205-ubuntu-font-family-0.83.zip
sudo mkdir -p /usr/share/fonts/truetype/ubuntu
sudo mv ubuntu-font-family-0.83/*.* /usr/share/fonts/truetype/ubuntu
```

## Install Pillow Library

```bash
sudo apt-get install python3-pil
```

## Install NumPy Library

```bash
sudo apt-get install python3-numpy
```

You're all set. Go back to the [readme](README.md) for remaining installation and documentation.


## Run your own node

Personally, I go with [Stadicus Raspibolt](https://stadicus.github.io/RaspiBolt/), but there are plenty of other good nodes, and handy guides to get started.  Check out the [node.guide](https://node.guide/) by Bitcoin Q+A

## Setup Run the Numbers

The [Run The Numbers](https://github.com/lucasmoten/runthenumbers/blob/main/runthenumbers) service is referenced by the scripts.  Feel free to reach out if you need help setting this up.