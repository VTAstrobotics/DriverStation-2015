#! /usr/bin/env python

import time
import struct
import socket as so
import pygame
from crc16pure import crc16xmodem

ControlData_format = '<B'
win_size = (500, 50)

running = True
key_text = ''
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
    global key_text
    k = pygame.key.name(event.key)
    key_text = k
    update_control(k, event.type == pygame.KEYDOWN)
    send_data(control)

def render():
    screen.fill((223, 223, 223))

    help_label = font.render("Press arrow keys to transmit", True, (0, 0, 0))
    help_rect = help_label.get_rect()
    help_rect.midtop = (win_size[0] / 2, 4)
    screen.blit(help_label, help_rect)

    key_label = font.render(key_text, True, (0, 0, 0))
    key_rect = key_label.get_rect()
    key_rect.midbottom = (win_size[0] / 2, win_size[1] - 4)
    screen.blit(key_label, key_rect)

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

pygame.init()
screen = pygame.display.set_mode(win_size)
pygame.display.set_caption("Astrobotics 2015 Driver Station")
font = pygame.font.Font(None, 22)
pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keyevent(event)

    render()
    pygame.display.flip()
    time.sleep(0.01)
