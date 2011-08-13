import sys
import time
import pygame
from pygame.locals import *

import chippy

FACTOR = 8

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
            if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
                if event.key == K_ESCAPE:
                    sys.exit(0)

                if event.key in KEYS:
                    i = KEYS.index(event.key)
                    if event.type == pygame.KEYDOWN:
                        self.buttons[i] = True
                    elif event.type == pygame.KEYUP:
                        self.buttons[i] = False

    def clear(self):
        self.buf = [[False] * chippy.RESY for _ in range(chippy.RESX)]
        self.screen.fill(CLEAN, (0, 0, chippy.RESX * FACTOR, chippy.RESY * FACTOR))

    def invert_pixel(self, x, y):
        #print x, y
        #print len(self.buf), len(self.buf[0])
        value = not self.buf[x][y]
        self.buf[x][y] = value

        color = ACTIVE if value else CLEAN

        self.screen.fill(color, (x * FACTOR, y * FACTOR, FACTOR, FACTOR))

        return not value

    def update(self):
        pygame.display.flip()

    def wait_key(self, key):
        while True:
            self.handle_input()

            if self.buttons[key]:
                return True
            else:
                time.sleep(0.01)

    def key(self, key):
        self.handle_input()
        #print self.buttons
        return self.buttons[key]

ui = PygameUi()
emu = chippy.Chip8(sys.argv[1], ui)
emu.run()

