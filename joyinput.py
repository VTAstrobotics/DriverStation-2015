# Handles joystick/gamepad input
# Takes care of translating both Xbox and regular
# USB gamepad controls to a common format
# -*- coding: utf-8 -*-

import os
from threading import Thread
import pygame

class JoyControls(object):
        LTHUMBX = 0
        LTHUMBY = 1
        RTHUMBX = 2
        RTHUMBY = 3
        RTRIGGER = 4
        LTRIGGER = 5
        A = 6
        B = 7
        X = 8
        Y = 9
        LB = 10
        RB = 11
        BACK = 12
        START = 13
        XBOX = 14
        LTHUMBBTN = 15
        RTHUMBBTN = 16
        DPAD = 17
        L2 = 18
        R2 = 19

class ControlMapXbox(object):
    """ Control map for Xbox controllers, should be using
        the xboxdrv userspace driver """
        
    axes = {0: JoyControls.LTHUMBX,
            1: JoyControls.LTHUMBY,
            2: JoyControls.RTHUMBX,
            3: JoyControls.RTHUMBY,
            4: JoyControls.RTRIGGER,
            5: JoyControls.LTRIGGER}
    
    buttons = {0: JoyControls.A,
               1: JoyControls.B,
               2: JoyControls.X,
               3: JoyControls.Y,
               4: JoyControls.LB,
               5: JoyControls.RB,
               6: JoyControls.BACK,
               7: JoyControls.START,
               8: JoyControls.XBOX,
               9: JoyControls.LTHUMBBTN,
               10: JoyControls.RTHUMBBTN}

class ControlMapHID(object):
    """ Control map for regular USB (HID) gamepads """
    
    axes = {0: JoyControls.LTHUMBX,
            1: JoyControls.LTHUMBY,
            2: JoyControls.RTHUMBX,
            3: JoyControls.RTHUMBY}
    
    buttons = {0: JoyControls.X,
               1: JoyControls.A,
               2: JoyControls.B,
               3: JoyControls.Y,
               4: JoyControls.LB,
               5: JoyControls.RB,
               6: JoyControls.L2,
               7: JoyControls.R2,
               8: JoyControls.BACK,
               9: JoyControls.START,
               10: JoyControls.LTHUMBBTN,
               11: JoyControls.RTHUMBBTN}

class JoyInput(Thread):
    def __init__(self, joyIndex=0, deadzone=0.1, callback=None):
        Thread.__init__(self)
        self.joyIndex = joyIndex
        self.deadzone = deadzone
        self.callback = callback
        self.running = False
        
        # Setup pygame
        # Pygame must have a display created to use joysticks,
        # so use the dummy video driver to avoid needing a GUI
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))
        # Initialize joystick
        pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(joyIndex)
        self.joy.init()
        
        # Figure out joystick type and assign appropriate map
        if 'Xbox' in self.joy.get_name():
            self.map = ControlMapXbox
        else:
            self.map = ControlMapHID 
    
    def run(self):
        self.running = True
        
        while(self.running):
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self._handle_axis(event.axis, event.value)
                elif event.type == pygame.JOYHATMOTION:
                    self._handle_dpad(event.value)
                elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    self._handle_button(event.button, event.type)

    def _handle_axis(self, axis, value):
        if axis not in self.map.axes:
            return
        if abs(value) < self.deadzone:
            value = 0
        self._fire(self.map.axes[axis], value)
        
    def _handle_dpad(self, value):
        self._fire(JoyControls.DPAD, value)
    
    def _handle_button(self, buttonId, eventType):
        if buttonId not in self.map.buttons:
            return
        value = 1 if eventType == pygame.JOYBUTTONDOWN else 0
        self._fire(self.map.buttons[buttonId], value)
        
    def _fire(self, controlId, value):
        if self.callback:
            self.callback(controlId, value)
        
    def stop(self):
        self.running = False
