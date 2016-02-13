#! /usr/bin/env python
# -*- coding: utf-8 -*-

# 2015 Python driver station for Astrobotics
# Run with python 2

import os
import time
import struct
import socket as so
from datetime import datetime
import threading
import logging.handlers
import foscam
from crc16pure import crc16xmodem
from joyinput import JoyInput, JoyControls, clamp

ControlData_format = '<BB'
PingData_format = '<B'

robot_ip = '10.0.0.30'
camera_ip = '10.0.0.51'
control_port = 6800
ping_port = 6900
ping_value = 216
ping_stop = threading.Event()

log_filepath = '%s/%s' % (os.path.expanduser('~'), 'logs/ds-log')
log_size = 1024*1024*10 # 10 MiB
log_count = 4           # 4 log files

camera = foscam.Camera('VTAstrobot', 'RoVER16', camera_ip)

def ping_thread_entry():
    while not ping_stop.is_set():
        data = struct.pack(PingData_format, ping_value)
        ping_sock.sendto(data, (robot_ip, ping_port))
        time.sleep(1)

def handler(controlId, value):
    # Format axis data
    if controlId <= JoyControls.LTRIGGER:
        # NOTE: The triggers have range [0, 100] instead of [-100, 100]
        # So the final value that is sent will have range [90, 180] instead of [0, 180]
        value = clamp(0, 180, int((value + 1) * 90))
    # Format dpad data
    elif controlId == JoyControls.DPAD:
        # DPAD is 4 groups of 2 bits: +Y -Y +X -X
        camera.exec_command(value)
        value = (int(value[0] < 0)) \
              | (int(value[0] > 0) << 2) \
              | (int(value[1] < 0) << 4) \
              | (int(value[1] > 0) << 6)
    control_name = [x for x in JoyControls.__dict__ if JoyControls.__dict__[x] == controlId][0]
    debug_str = '%s = %s' % (control_name, value)
    print(debug_str)
    logger.debug(debug_str)
    send_data(controlId, value)

joy = JoyInput(joyIndex=0, deadzone=0.1, callback=handler)

def send_data(controlId, value):
    data = [controlId, value]
    data_bare = struct.pack(ControlData_format, *data)
    crc16 = crc16xmodem(data_bare)
    data.append(crc16)
    data = struct.pack(ControlData_format + 'H', *data)
    sock.sendto(data, (robot_ip, control_port))

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

ping_sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
ping_sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)
ping_sock.bind(('0.0.0.0', ping_port))

# Log file
log_dir = os.path.dirname(log_filepath)
if not os.path.isdir(log_dir):
    os.mkdir(os.path.dirname(log_filepath))
logger = logging.getLogger('ds-2015')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.handlers.RotatingFileHandler(log_filepath, maxBytes=log_size, backupCount=log_count))
logger.info('\n\n---- Starting DS Log - %s ----' % datetime.now().ctime())

try:
#     camera.exec_command((1, 0))
    joy.start()
    ping_thread = threading.Thread(target=ping_thread_entry, name='Ping Thread')
    ping_thread.setDaemon(True)
    ping_thread.start()
    print("Controller started")
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    print("Exiting")
finally:
    joy.stop()
    ping_stop.set()
    sock.close()
    ping_sock.close()

exit()