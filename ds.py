#! /usr/bin/env python

import struct
import socket as so
import Tkinter as tk
from crc16pure import crc16xmodem

ControlData_format = '<B'

control = {'up': False, 'down': False, 'left': False, 'right': False}

def update_control(k, pressed):
	k = k.lower()
	if k in control:
		control[k] = pressed

def send_data(data):
	dir_data = int(data['up']) | (int(data['down']) << 1) | (int(data['left']) << 2) | (int(data['right']) << 3)
	data_bare = struct.pack(ControlData_format, dir_data)
	crc16 = crc16xmodem(data_bare)
	data = struct.pack(ControlData_format + 'H', dir_data, crc16)
	sock.sendto(data, ('192.168.0.2', 6800))

def keyevent(event):
	k = event.keysym
	key_text.set(k)
	update_control(k, event.type == '2') # KeyPress = 2
	send_data(control)

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

root = tk.Tk()
root.geometry('500x50')
label = tk.Label(root, text="Press arrow keys to transmit", font=('', 14))
key_text = tk.StringVar()
key_label = tk.Label(root, textvariable=key_text, font=('', 14))
label.pack()
key_label.pack()
root.bind('<KeyPress>', keyevent)
root.bind('<KeyRelease>', keyevent)
root.mainloop()
