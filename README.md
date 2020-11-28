# pizero-minipitft

Scripts for Adafruit Mini Pi TFT

- [bitcoin.py](bitcoin.py) - A script with multiple panels to display assorted bitcoin related interests.  Currently focused on mempool and sats per byte to get in next 2 blocks


This is an initial guide for how to setup this project on a Raspberry Pi Zero

Here are the parts used for this project
- [Raspberry Pi Zero W](https://www.adafruit.com/product/3400) $10.00 USD
- [2x20 pin Header](https://www.adafruit.com/product/2822) $0.95 USD
- [Mini PiTFT 135x240 Color TFT](https://www.adafruit.com/product/4393) $14.95 USD


## Initial setup of Raspberry Pi

This is based in part on https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup. 

You will need a Raspberry Pi Zero W.  Alternatively you can use a heftier Pi3B or Pi4B but it's not necessary for this project.

Use Raspberry Pi Imager to install Raspbian Lite 

Activate SSH support and setup your wifi connection by editing the wpa_supplicant.conf

SSH into the pi once you've identified which device it is on the network

Default credentials are 
- username: pi
- password: raspberry

You should change those

Once logged in, run the following

```bash
sudo raspi-config
```

And enable the I2C and SPI interfaces.
Save and exit, and reboot the pi.

```
sudo reboot now
```

And then SSH back in.

## Install CircuitPython Libraries on Raspberry Pi

This project depends on Python and assorted libraries

Follow instructions here:
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

Which 

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

## Download the Script and files

Clone the repo

```bash
cd ~/
git clone git@github.com:lucasmoten/pizero-minipitft.git
cd ~/pizero-minipitft
```

Review/Edit

```bash
nano bitcoin.py
```
If you have your own mempool server you can change the API endpoint at the top


Test run

```bash
cd ~/pizero-minipitft
sudo python3 bitcoin.py
```

Press CTRL+C to cancel the process. 

