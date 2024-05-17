#!/usr/bin/python3

'''
- Raspberry Pi Zero W
https://my.cytron.io/p-raspberry-pi-zero-w-and-bundles
- Raspberry Pi Camera Module 3 - 12MP with Auto Focus lens
https://my.cytron.io/p-raspberry-pi-camera-module-3-12mp-with-auto-focus-lens
- Raspberry Pi Zero/W/WH 15cm Camera Cable
https://my.cytron.io/p-raspberry-pi-zero-v1.3-camera-cable
Increase SWAP size to 2048
https://pimylifeup.com/raspberry-pi-swap-file/
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt-get install libqt5gui5 libqt5test5 python3-sip python3-pyqt5 libjasper-dev libatlas-base-dev -y
pip3 install opencv-contrib-python==4.8.0.74
sudo modprobe bcm2835-v4l2
pip3 install pyzbar
sudo reboot
'''

import cv2
from pyzbar.pyzbar import decode

from picamera2 import MappedArray, Picamera2, Preview
from libcamera import controls
from libcamera import Transform

colour = (0, 255, 0)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2

def draw_barcodes(request):
    with MappedArray(request, "main") as m:
        for b in barcodes:
            if b.polygon:
                x = min([p.x for p in b.polygon])
                y = min([p.y for p in b.polygon]) - 30
                cv2.putText(m.array, b.data.decode('utf-8'), (x, y), font, scale, colour, thickness)

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
config = picam2.create_preview_configuration(main={"size": (640, 480)}, transform=Transform(hflip=True, vflip=True))
picam2.configure(config)


barcodes = []
picam2.post_callback = draw_barcodes
picam2.start()

picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 8.0})

while True:
    rgb = picam2.capture_array("main")
    barcodes = decode(rgb)
