import uos
import time
import sys
from machine import I2C, Pin
from gfx_pack import SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E, GfxPack

y = 0
ready = False

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

def list_files(path="/"):
    scripts = []
    try:
        entries = uos.listdir(path)
    except OSError:
        return scripts

    for name in entries:
        if not name.endswith(".py") or name == "main.py":
            continue
        full = path.rstrip("/") + "/" + name
        try:
            st = uos.stat(full)
        except OSError:
            continue
        if st[0] & 0x4000:
            continue
        scripts.append(name[:-3])
    return scripts

def poll_and_print():
    global last, ready, y
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

            displacement = 30
            if name == "-" and state == "pressed":
                if backlight["w"] > displacement + 1:
                    backlight["w"] -= displacement
                gp.set_backlight(**backlight)

            if name == "+" and state == "pressed":
                if backlight["w"] < 256 - displacement:
                    backlight["w"] += displacement
                gp.set_backlight(**backlight)

            if ready:
                if name == "x" and state == "pressed":
                    if len(list_files("/")) * 12 <= y * 12:
                        y -= 12
                if name == "b" and state == "pressed":
                    y += 12
                if name == "a" and state == "pressed":
                    files = list_files("/")
                    idx = y // 12
                    if 0 <= idx < len(files):
                        run_and_exit(files[idx] + ".py")

            if name == "a" and state == "pressed":
                ready = True

    last = data
    time.sleep_ms(30)

def printfiles():
    global y
    files = list_files("/")
    if not files:
        return

    display.set_pen(15)
    for row, filepath in enumerate(files):
        y_pos = row * 12 - y
        if row == y / 12:
            display.set_pen(0)
        else:
            display.set_pen(15)
        display.text(filepath, 10, y_pos)
    display.update()

def run_and_exit(path):
    with open(path, "r") as f:
        code = f.read()
    exec(code, globals())
    raise SystemExit("Swapped to {}".format(path))

def start():
    global ready
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    display.text("Welcome!", 20, 10)
    display.rectangle(35, 36, 55, 20)
    display.set_pen(0)
    display.text("play", 40, 40)
    display.update()
    while True:
        poll_and_print()
        if ready:
            break

start()

while True:
    poll_and_print()
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    display.rectangle(0, 0, 128, 12)
    printfiles()
    display.update()

