import re
import random
import time

RESX = 64
RESY = 32

class Chip8:

    def __init__(self, fn, ui):
        self.ui = ui

        # internals
        self.pc = 0x200
        self.stack = []
        self.memory = [0] * 0x1000

        # registers
        self.i = 0
        self.r = [0] * 16

        # timers
        self.sound = 0
        self.delay = (0, 0)

        # load the game
        self.load_file(fn)
        self.init_fonts()

    def init_fonts(self):
        fonts = []

        # 0
        fonts.extend([0xf0, 0x09, 0x09, 0x09, 0xf0])
        # 1
        fonts.extend([0x20, 0x60, 0x20, 0x20, 0x70])
        # 2
        fonts.extend([0xf0, 0x10, 0xf0, 0x80, 0xf0])
        # 3
        fonts.extend([0xf0, 0x10, 0xf0, 0x10, 0xf0])
        # 5
        fonts.extend([0x90, 0x90, 0xf0, 0x10, 0x10])
        # 6
        fonts.extend([0xf0, 0x80, 0xf0, 0x90, 0xf0])
        # 7
        fonts.extend([0xf0, 0x10, 0x20, 0x40, 0x40])
        # 8
        fonts.extend([0xf0, 0x90, 0xf0, 0x90, 0xf0])
        # 9
        fonts.extend([0xf0, 0x90, 0xf0, 0x10, 0xf0])
        # a
        fonts.extend([0xf0, 0x90, 0xf0, 0x90, 0x90])
        # b
        fonts.extend([0xe0, 0x90, 0xe0, 0x90, 0xe0])
        # c
        fonts.extend([0xf0, 0x80, 0x80, 0x80, 0xf0])
        # d
        fonts.extend([0xe0, 0x90, 0x90, 0x90, 0xe0])
        # e
        fonts.extend([0xf0, 0x80, 0xf0, 0x80, 0xf0])
        # f
        fonts.extend([0xf0, 0x80, 0xf0, 0x80, 0x80])

        self.memory[0:len(fonts)] = fonts

    def load_file(self, fn):
        f = open(fn)
        raw = f.read()
        f.close()

        self.memory[0x200:0x200+len(raw)] = (ord(i) for i in raw)

    def sub_ret(self):
        addr = self.stack.pop()
        self.jump(addr)

    def jump(self, addr):
        self.pc = addr 

    def call(self, addr):
        self.stack.append(self.pc)
        self.pc = addr

    def skip(self, ):
        self.pc += 2

    def s_eval(self, reg, n):
        if self.r[reg] == n:
            self.skip()

    def s_uneval(self, reg, n):
        if self.r[reg] != n:
            self.skip()

    def s_r_eval(self, a, b):
        if self.r[a] == self.r[b]:
            self.skip()

    def s_r_uneval(self, a, b):
        if self.r[a] != self.r[b]:
            self.skip()

    def off_jump(self, n):
        self.pc = n + self.r[0]

    def put_sound(self, n):
        # TODO
        self.sound = n

    def put_delay(self, reg):
        self.delay = (self.r[reg], time.time())
        print self.delay

    def get_delay(self, reg):
        val, start = self.delay
        cur = int(val - (time.time() - start) * 60)
        print "delay:", cur, "@", time.time()
        self.r[reg] = max(cur, 0)

    def put_i(self, n):
        self.i = n

    def put_bcd(self, reg):
        i = self.i
        n = self.r[reg]
        memory = self.memory

        memory[i] = (n / 100)
        memory[i+1] = (n / 10) % 10
        memory[i+2] = n % 100

    def put_register(self, reg, n):
        self.r[reg] = n

    def add_register(self, reg, n):
        self.r[reg] += n

    def add_r_i(self, reg):
        self.i += self.r[reg]

    def copy_register(self, a, b):
        self.r[a] = self.r[b]

    def or_register(self, a, b):
        self.r[a] |= self.r[b]

    def and_register(self, a, b):
        self.r[a] &= self.r[b]

    def xor_register(self, a, b):
        self.r[a] ^= self.r[b]

    def add_r_register(self, a, b):
        self.r[a] += self.r[b]

        if self.r[a] > 255:
            self.r[a] %= 255
            self.r[0xf] = 1
        else:
            self.r[0xf] = 0

    def sub_r_register(self, a, b):
        self.r[a] -= self.r[b]

        if self.r[a] < 9:
            self.r[a] %= 255
            self.r[0xf] = 0
        else:
            self.r[0xf] = 1

    def subn_r_register(self, a, b):
        self.r[a] = self.r[b] - self.r[a]

        if self.r[a] < 9:
            self.r[a] %= 255
            self.r[0xf] = 0
        else:
            self.r[0xf] = 1

    def rshift_register(self, reg, _):
        self.r[0xf] = self.r[reg] & 1
        self.r[reg] >>= 1

    def lshift_register(self, reg, _):
        v = self.r[reg]
        self.r[0xf] = v & 0x80 << 8
        self.r[reg] = v << 1 & 0xff

    def store_registers(self, reg):
        size = reg + 1
        i = self.i
        self.memory[i:i+size] = self.r[0:size]

    def restore_registers(self, reg):
        size = reg + 1
        i = self.i
        self.r[0:size] = self.memory[i:i+size]

    def and_random(self, reg, n):
        self.r[reg] = n & random.randint(0x00, 0xff)

    def draw_sprite(self, a, b, height):
        i = self.i
        y = self.r[b]

        erase = False

        for line in self.memory[i:i+height]:
            x = self.r[a]

            for _ in range(8):
                if line >> 7 & 1:
                    erase |= self.ui.invert_pixel(x % RESX, y % RESY)

                line <<= 1
                x += 1

            y += 1

        self.ui.update()

        self.r[0xf] = 1 if erase else 0

    def get_letter(self, reg):
        self.i = self.r[reg] * 5

    def s_key_down(self, reg):
        if self.ui.key(self.r[reg]):
            self.skip()

    def s_key_up(self, reg):
        if not self.ui.key(self.r[reg]):
            self.skip()

    def run(self):
        memory = self.memory

        while True:
            raw_code = memory[self.pc:self.pc+2]
            code = ("%02x"*2 % tuple(raw_code)).upper()

            #print code

            self.pc += 2

            self.opcode(code)

            #for i, r in enumerate(self.r):
                #print "%2x: %02x" % (i, r)

            #print " i: %02x" % self.i
            #print "pc: %3x" % self.pc

            #raw_input()

            time.sleep(0.001)

    def opcode(self, cur):
        codes = {
                '00E0': self.ui.clear,
                '00EE': self.sub_ret,
                '1(...)': self.jump,
                '2(...)': self.call,
                '3(.)(..)': self.s_eval,
                '4(.)(..)': self.s_uneval,
                '5(.)(.)0': self.s_r_eval,
                '6(.)(..)': self.put_register,
                '7(.)(..)': self.add_register,
                '8(.)(.)0': self.copy_register,
                '8(.)(.)1': self.or_register,
                '8(.)(.)2': self.and_register,
                '8(.)(.)3': self.xor_register,
                '8(.)(.)4': self.add_r_register,
                '8(.)(.)5': self.sub_r_register,
                '8(.)(.)6': self.rshift_register,
                '8(.)(.)7': self.subn_r_register,
                '8(.)(.)E': self.lshift_register,
                '9(.)(.)0': self.s_r_uneval,
                'A(...)': self.put_i,
                'B(...)': self.off_jump,
                'C(.)(..)': self.and_random,
                'D(.)(.)(.)': self.draw_sprite,
                'E(.)9E': self.s_key_down,
                'E(.)A1': self.s_key_up,
                'F(.)07': self.get_delay,
                'F(.)0A': self.ui.wait_key,
                'F(.)15': self.put_delay,
                'F(.)18': self.put_sound,
                'F(.)1E': self.add_r_i,
                'F(.)29': self.get_letter,
                'F(.)33': self.put_bcd,
                'F(.)55': self.store_registers,
                'F(.)65': self.restore_registers,
                }

        for opcode, fun in codes.items():
            match = re.match(opcode + "$", cur)

            if match:
                args = (int(i, 16) for i in match.groups())
                fun(*args)
                break
        else:
            print "opcode %s not found!" % opcode
            raw_input()

