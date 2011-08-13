import sys
import time
import pygame
from pygame.locals import *

import chippy

FACTOR = 4

ACTIVE = (0xff,)*3
CLEAN = (0x00,)*3

KEYS = [
        K_x,
        K_1, K_2, K_3,
        K_q, K_w, K_e,
        K_a, K_s, K_d,
        K_z, K_c,
        K_4, K_r, K_f, K_v,
        ]

class PygameUi:

    def __init__(self):
        self.screen = pygame.display.set_mode((chippy.RESX * FACTOR, chippy.RESY * FACTOR))
        self.buttons = [False] * 16

        self.clear()

    def handle_input(self):
        for event in pygame.event.get():
            if event.key == ESCAPE:
                sys.exit(0)

            name = pygame.key.get_name()
            print name
            raw_input()
            if event.key in KEYS:
                i = KEYS.indexof(eveny.key)
                if event.type == KEYDOWN:
                    self.buttons[i] = True
                elif event.type == KEYUP:
                    self.buttons[i] = True

    def clear(self):
        self.buf = [[False] * chippy.RESY for _ in range(chippy.RESX)]
        self.screen.fill(CLEAN, (0, 0, chippy.RESX * FACTOR, chippy.RESY * FACTOR))

    def invert_pixel(self, x, y):
        print x, y
        print len(self.buf), len(self.buf[0])
        value = not self.buf[x][y]
        self.buf[x][y] = value

        color = ACTIVE if value else CLEAN

        self.screen.fill(color, (x * FACTOR, y * FACTOR, FACTOR, FACTOR))

        return not value

    def update(self):
        pygame.display.flip()

    def wait_key(self):
        raw_input()
        handle_input()
        print "wait for key not implemented"

    def key(self, key):
        raw_input()
        handle_input()
        return self.buttons[key]

ui = PygameUi()
emu = chippy.Chip8(sys.argv[1], ui)
emu.run()

