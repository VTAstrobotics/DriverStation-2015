#! /usr/bin/env python

import struct
import socket as so
import Tkinter as tk
from crc16pure import *

ControlData_format = '<B'

def send_data(up, down, left, right):
	dir_data = int(up) | (int(down) << 1) | (int(left) << 2) | (int(right) << 3)
	data_bare = struct.pack(ControlData_format, dir_data)
	crc16 = crc16xmodem(data_bare)
	data = struct.pack(ControlData_format + 'H', dir_data, crc16)
	sock.sendto(data, ('192.168.0.2', 6800))

def keypress(event):
	k = event.keysym
	key_text.set(k)
	send_data(k == 'Up', k == 'Down', k == 'Left', k == 'Right')

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

root = tk.Tk()
root.geometry('500x50')
label = tk.Label(root, text = "Press arrow keys to transmit", font = ('', 14))
key_text = tk.StringVar()
key_label = tk.Label(root, textvariable = key_text, font = ('', 14))
label.pack()
key_label.pack()
root.bind('<KeyPress>', keypress)
root.mainloop()
