#! /usr/bin/env python
# -*- coding: utf-8 -*-

# 2015 Python driver station for Astrobotics
# Should support both python 2 and 3

import time
import struct
import socket as so
from crc16pure import crc16xmodem
from joyinput import JoyInput, JoyControls

ControlData_format = '<BB'

def clamp(minN, maxN, N):
    return max(min(maxN, N), minN)

def handler(controlId, value):
    # Format axis data
    if controlId <= JoyControls.LTRIGGER:
        # NOTE: The triggers have range [0, 100] instead of [-100, 100]
        # So the final value that is sent will have range [90, 180] instead of [0, 180]
        value = clamp(0, 180, int((value + 1) * 90))
    # Format dpad data
    elif controlId == JoyControls.DPAD:
        # DPAD is 4 groups of 2 bits: +Y -Y +X -X
        value = (int(value[0] < 0)) \
              | (int(value[0] > 0) << 2) \
              | (int(value[1] < 0) << 4) \
              | (int(value[1] > 0) << 6)
    print(controlId,value)
    send_data(controlId, value)

joy = JoyInput(joyIndex = 0, deadzone = 0.2, callback = handler)

def send_data(controlId, value):
    data = [controlId, value]
    data_bare = struct.pack(ControlData_format, *data)
    crc16 = crc16xmodem(data_bare)
    data.append(crc16)
    data = struct.pack(ControlData_format + 'H', *data)
    sock.sendto(data, ('10.0.0.30', 6800))

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

try:
    joy.start()
    print("Controller started")
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    print("Exiting")
finally:
    joy.stop()

exit()
