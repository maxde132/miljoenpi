import ujson as json
import uos
import time
from machine import I2C, Pin
from gfx_pack import SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E, GfxPack

SCORES_FILE = "scores.json"

x = 50
y = 60
score = 0

ballx = 10
bally = 10
oldx = 1
oldy = 1
oldpaddlex = 1
oldpaddley = 1

has_crashed = False
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


def drawball(x, y):
    global oldx, oldy
    display.set_pen(0)
    display.line(oldx, oldy, oldx + 5, oldy)
    display.line(oldx + 5, oldy, oldx + 5, oldy + 5)
    display.line(oldx, oldy + 5, oldx + 6, oldy + 5)
    display.line(oldx, oldy + 5, oldx, oldy)
    display.set_pen(15)
    display.line(x, y, x + 5, y)
    display.line(x + 5, y, x + 5, y + 5)
    display.line(x, y + 5, x + 6, y + 5)
    display.line(x, y + 5, x, y)
    oldx = x
    oldy = y


def drawpaddle(x, y):
    global oldpaddlex, oldpaddley
    display.set_pen(0)
    display.line(oldpaddlex, oldpaddley, oldpaddlex + 20, oldpaddley)
    display.line(oldpaddlex, oldpaddley - 1, oldpaddlex + 20, oldpaddley - 1)
    oldpaddlex = x
    oldpaddley = y
    display.set_pen(15)
    display.line(x, y, x + 20, y)
    display.line(x, y - 1, x + 20, y - 1)


def reset():
    global x, y, score, ballx, bally, oldx, oldy, oldpaddlex, oldpaddley, has_crashed
    has_crashed = False
    x, y = 50, 60
    score = 0
    ballx, bally = 10, 10
    oldx, oldy = 1, 1
    oldpaddlex, oldpaddley = 1, 1
    display.set_pen(0)
    display.clear()
    display.set_pen(15)


def poll_and_print():
    global last, x, y
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
            if not (changed & (1 << bit)):
                continue

            name = BUTTON_MAP.get((0x00, byte_idx, bit))
            if not name:
                continue

            val = (data[byte_idx] >> bit) & 1
            state = "pressed" if val == 0 else "released"

            display.set_pen(0)
            display.set_pen(15)

            if name == "r" and state == "pressed":
                reset()

            disp = 30
            if name == "-" and state == "pressed":
                if backlight["w"] > disp + 1:
                    backlight["w"] -= disp
                gp.set_backlight(**backlight)

            if name == "+" and state == "pressed":
                if backlight["w"] < 256 - disp:
                    backlight["w"] += disp
                gp.set_backlight(**backlight)

            if name == "a" and state == "pressed":
                x += 10
            if name == "y" and state == "pressed":
                x -= 10

    last = data
    time.sleep_ms(30)


def move_ball(speed):
    global ballx, bally, diagonal, up, x, y, score, has_crashed
    if not has_crashed:
        screen_w, screen_h = display.get_bounds()
        if ballx <= 0:
            diagonal = 1
        if ballx >= screen_w - 5:
            diagonal = -1
        if bally <= 0:
            up = 1
        if (x <= ballx <= x + 20) and (y - 1 <= bally + 5 <= y + 1):
            up = -1
            score += 1
        ballx += diagonal * speed
        bally += up * speed
        drawball(ballx, bally)


def load_scores():
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_score(game_name, score):
    try:
        with open(SCORES_FILE, "r") as f:
            scores = json.load(f)
    except (OSError, ValueError):
        scores = {}
    scores[game_name] = score
    temp_path = SCORES_FILE + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(scores, f)
    uos.rename(temp_path, SCORES_FILE)


def updatehighscore(score):
    current = load_scores().get("pong", 0)
    if score > current:
        save_score("pong", score)


def displayscore():
    global score
    display.set_pen(0)
    display.rectangle(109, 0, 109, 12)
    display.set_pen(15)
    display.text(str(score), 109, 0)


def gameover():
    global has_crashed
    if has_crashed and bally > 70:
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Game over", 20, 10)
        display.text("score:" + str(score), 20, 30)
        updatehighscore(score)
        display.text("high:" + str(load_scores().get("pong", 0)), 20, 50)
        time.sleep_ms(30)


while True:
    poll_and_print()
    drawpaddle(x, y)
    displayscore()
    move_ball(1)
    if bally > 70 and ballx != 10:
        has_crashed = True
    gameover()
    display.update()
    time.sleep(0.005)

