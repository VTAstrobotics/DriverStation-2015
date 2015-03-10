#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import struct
import socket as so
import pygame
from crc16pure import crc16xmodem

# GUI constants
font_color = (0, 0, 0)
win_size = (500, 50)
padding = 4
arrow_block_size = 40

# GUI stuff
running = True

# Control data
ControlData_format = '<B'
control = {'teleop': False, 'up': False, 'down': False, 'left': False, 'right': False}

def update_control(k, pressed):
    k = k.lower()
    if k in control:
        control[k] = pressed

def send_data(data):
    bitfield = (int(data['teleop'])) \
             | (int(data['up']) << 1) \
             | (int(data['down']) << 2) \
             | (int(data['left']) << 3) \
             | (int(data['right']) << 4)
    data_bare = struct.pack(ControlData_format, bitfield)
    crc16 = crc16xmodem(data_bare)
    data = struct.pack(ControlData_format + 'H', bitfield, crc16)
    sock.sendto(data, ('192.168.0.2', 6800))

def keyevent(event):
    global key_text
    k = pygame.key.name(event.key)
    if k == 't' and event.type == pygame.KEYDOWN:
        control['teleop'] = not control['teleop']
    else:
        update_control(k, event.type == pygame.KEYDOWN)
    send_data(control)

def render_arrow_block(char, fromright, active):
    if active:
        color = font_color
    else:
        color = [0xBB] * 3
    label = arrow_font.render(char, True, color)
    rect = label.get_rect()
    rect.midbottom = (win_size[0] - padding - arrow_block_size * (fromright + 0.5), win_size[1] - padding)
    screen.blit(label, rect)

def render():
    screen.fill((223, 223, 223))

    help_label = font.render("Press arrow keys to transmit", True, font_color)
    help_rect = help_label.get_rect()
    help_rect.midtop = (win_size[0] / 2, padding)
    screen.blit(help_label, help_rect)

    teleop_text = "Teleop" if control['teleop'] else "Autonomous"
    teleop_label = font.render("Mode: %s" % teleop_text, True, font_color)
    teleop_rect = teleop_label.get_rect()
    teleop_rect.bottomleft = (padding, win_size[1] - padding)
    screen.blit(teleop_label, teleop_rect)

    render_arrow_block(u'↑', 3, control['up'])
    render_arrow_block(u'↓', 2, control['down'])
    render_arrow_block(u'←', 1, control['left'])
    render_arrow_block(u'→', 0, control['right'])

sock = so.socket(so.AF_INET, so.SOCK_DGRAM)
sock.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

pygame.init()
screen = pygame.display.set_mode(win_size)
pygame.display.set_caption("Astrobotics 2015 Driver Station")
font = pygame.font.SysFont('Verdana', 13)
arrow_font = pygame.font.SysFont('Arial', 18)
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
