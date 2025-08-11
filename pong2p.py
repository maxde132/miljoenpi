# Apologies in advance, i got my rights and lefts mixed up in this script lol

import time
import ujson as json
import uos
from machine import I2C, Pin
from gfx_pack import SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E, GfxPack

SCORES_FILE = "scores.json"

gameover = False
scorel = 0
scorer = 0
lpaddley = 25
rpaddley = 25

ballx = 10
bally = 10
oldx = 1
oldy = 1
oldpaddlex = 1
oldpaddley = 1

diagonal = 1
up = 1

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
ADDR = 0x21

gp = GfxPack()
gp.set_backlight(0, 0, 0, 100)
display = gp.display
backlight = {"r": 0, "g": 0, "b": 0, "w": 255}

BUTTON_MAP = {
    (0x00, 1, 7): "x",
    (0x00, 1, 6): "a",
    (0x00, 1, 4): "b",
    (0x00, 1, 5): "y",
    (0x00, 0, 1): "u",
    (0x00, 0, 3): "r",
    (0x00, 0, 4): "d",
    (0x00, 0, 2): "l",
    (0x00, 0, 5): "-",
    (0x00, 1, 3): "+",
}

try:
    last = i2c.readfrom_mem(ADDR, 0x00, 2)
except OSError:
    last = bytes([0xFF, 0xFF])


def reset():
    global ballx, bally, gameover, scorer, scorel
    ballx, bally = 50, 25
    scorer, scorel = 0, 0
    gameover = False


def poll_and_print():
    global last, lpaddley, rpaddley
    try:
        data = i2c.readfrom_mem(ADDR, 0x00, 2)
    except OSError:
        time.sleep_ms(30)
        return

    for byte_idx in range(2):
        changed = data[byte_idx] ^ last[byte_idx]
        if not changed:
            continue
        for bit in range(8):
            if not changed & (1 << bit):
                continue
            name = BUTTON_MAP.get((0x00, byte_idx, bit))
            if not name:
                continue
            val = (data[byte_idx] >> bit) & 1
            state = "pressed" if val == 0 else "released"
            display.set_pen(0)
            display.set_pen(15)
            disp = 30
            if name == "-" and state == "pressed":
                if backlight["w"] > disp + 1:
                    backlight["w"] -= disp
                gp.set_backlight(**backlight)
            if name == "+" and state == "pressed":
                if backlight["w"] < 256 - disp:
                    backlight["w"] += disp
                gp.set_backlight(**backlight)
            if name == "x" and state == "pressed":
                lpaddley -= 10
            if name == "b" and state == "pressed":
                lpaddley += 10
            if name == "u" and state == "pressed":
                rpaddley -= 10
            if name == "d" and state == "pressed":
                rpaddley += 10
            if name == "r" and state == "pressed":
                reset()
    last = data
    time.sleep_ms(30)


def drawpaddle(y, left):
    if left:
        display.line(120, y, 120, y + 20)
        display.line(119, y, 119, y + 20)
    else:
        display.line(8, y, 8, y + 20)
        display.line(7, y, 7, y + 20)


display.set_pen(0)
display.clear()
display.set_pen(15)


def drawball(x, y):
    global oldx, oldy
    display.set_pen(15)
    display.line(x, y, x + 5, y)
    display.line(x + 5, y, x + 5, y + 5)
    display.line(x, y + 5, x + 6, y + 5)
    display.line(x, y + 5, x, y)
    oldx, oldy = x, y


def move_ball(speed):
    global ballx, bally, diagonal, up, lpaddley, rpaddley
    sw, sh = display.get_bounds()
    if 118 < ballx < 122:
        if lpaddley + 5 <= bally + 5 <= lpaddley + 25:
            diagonal *= -1
    if 6 < ballx < 10:
        if rpaddley + 5 <= bally + 5 <= rpaddley + 25:
            diagonal *= -1
    if bally <= 0:
        up = 1
    elif bally >= sh - 6:
        up = -1
    ballx += diagonal * speed
    bally += up * speed
    drawball(ballx, bally)


def drawscores(left_score, right_score):
    display.text(str(left_score), 80, 50)
    display.text(str(right_score), 40, 50)


def keepscore():
    global scorel, scorer, ballx, bally, diagonal, gameover
    if ballx < -2:
        scorel += 1
        ballx, bally = 50, 10
        diagonal *= -1
    if ballx > 130:
        scorer += 1
        ballx, bally = 50, 10
        diagonal *= -1
    if scorel > 5 or scorer > 5:
        gameover = True


def gameoverr():
    if gameover:
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Game over!", 10, 25)


while True:
    display.set_pen(0)
    display.clear()
    poll_and_print()
    display.set_pen(15)
    drawpaddle(lpaddley, True)
    drawpaddle(rpaddley, False)
    move_ball(1)
    keepscore()
    drawscores(scorel, scorer)
    gameoverr()
    display.update()
    time.sleep(0.005)

