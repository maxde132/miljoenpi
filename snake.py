from machine import I2C, Pin
import time
from gfx_pack import SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E, GfxPack
from machine import I2C, Pin
import sys
import ujson as json
import random
SCORES_FILE = "scores.json"
framestate = 1
score = 0
applex = 1
appley = 1
snake = [
    [50, 50], [55, 50]                      
]

snakedir = "up"
gameover = False


i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
ADDR = 0x21
gp = GfxPack()
gp.set_backlight(0, 0, 0, 100)
display = gp.display
backlight = {"r": 0, "g": 0, "b": 0,"w": 255}
BUTTON_MAP = {
    (0x00, 1, 7): "x",
    (0x00, 1, 6): "a",
    (0x00, 1, 4): "b",
    (0x00, 1, 5): "y",
    (0x00, 0, 1): "u",   # up
    (0x00, 0, 3): "r",   # right
    (0x00, 0, 4): "d",   # down
    (0x00, 0, 2): "l",   # left
    (0x00, 0, 5): "-",   # minus
    (0x00, 1, 3): "+",   # plus
}
try:
    last = i2c.readfrom_mem(ADDR, 0x00, 2)
except OSError:
    last = bytes([0xFF, 0xFF])
def poll_and_print():
    global last, snakedir
    
    try:
        data = i2c.readfrom_mem(ADDR, 0x00, 2)
    except OSError as e:
        
        time.sleep_ms(30)
        return

    for byte_idx in range(2):
        global x
        global y
        changed = data[byte_idx] ^ last[byte_idx]
        if changed:
            for bit in range(8):
                if changed & (1 << bit):
                    key = (0x00, byte_idx, bit)
                    name = BUTTON_MAP.get(key)
                    if name is not None:
                        val = (data[byte_idx] >> bit) & 1
                        state = "pressed" if val == 0 else "released"  
                        
                        display.set_pen(0)  
                        display.set_pen(15)
                        
                    if name=="r" and state == "pressed":
                        reset()
                        print("r")
                    displacement = 30
                    if name=="-" and state == "pressed":
                        if backlight["w"] > displacement+1:
                            backlight["w"]-=displacement
                        gp.set_backlight(backlight["r"], backlight["g"], backlight["b"], backlight["w"])
                    if name=="+" and state == "pressed":
                        
                        if backlight["w"] < 256-displacement:
                            backlight["w"]+=displacement
                        gp.set_backlight(backlight["r"], backlight["g"], backlight["b"], backlight["w"])
                    if name=="a" and state == "pressed":
                        snakedir = "right"
                    if name=="x" and state=="pressed":
                        snakedir = "up"
                    if name=="y" and state == "pressed":
                        snakedir = "left"
                    if name=="b" and state == "pressed":
                        snakedir = "down"
                        

    last = data
    time.sleep_ms(30)
    
def drawsnake():
    global snake
    for seg_x, seg_y in snake:
        #print(seg_x + seg_y)
        #display.rectangle(seg_x+5, seg_y+5, seg_x+10, seg_y+10)
        display.rectangle(seg_x + 5, seg_y + 5, 5, 5)

def movesnake():
    
    global snake, snakedir, gameover, framestate
    snakelength = len(snake)
    if framestate == 1:
        if snakedir == "right":
            snake.pop()
            newhead = [snake[0][0] + 5, snake[0][1] + 0]
            for seg_x, seg_y in snake:
                #print(seg_x + seg_y)
                #display.rectangle(seg_x + 5, seg_y + 5, 5, 5)
                if newhead[0] == seg_x and newhead[1] == seg_y:
                    gameover = True
                    print("steeeeeve")
            snake.insert(0, newhead)
        if snakedir == "left":
            snake.pop()
            newhead = [snake[0][0] - 5, snake[0][1] + 0]
            for seg_x, seg_y in snake:
                #print(seg_x + seg_y)
                #display.rectangle(seg_x + 5, seg_y + 5, 5, 5)
                if newhead[0] == seg_x and newhead[1] == seg_y:
                    gameover = True
                    print("steeeeeve")
            snake.insert(0, newhead)
        if snakedir == "up":
            snake.pop()
            newhead = [snake[0][0], snake[0][1] + -5]
            for seg_x, seg_y in snake:
                #print(seg_x + seg_y)
                #display.rectangle(seg_x + 5, seg_y + 5, 5, 5)
                if newhead[0] == seg_x and newhead[1] == seg_y:
                    gameover = True
                    print("steeeeeve")
            snake.insert(0, newhead)
        if snakedir == "down":
            snake.pop()
            newhead = [snake[0][0], snake[0][1] + 5]
            for seg_x, seg_y in snake:
                
                #display.rectangle(seg_x + 5, seg_y + 5, 5, 5)
                if newhead[0] == seg_x and newhead[1] == seg_y:
                    gameover = True
                    print("steeeeeve")
            snake.insert(0, newhead)
        if snake[0][0] > 120 or snake[0][0] < -5 or snake[0][1] < -5 or snake[0][1] > 55:
            gameover = True
def drawapple():
    
    global display, applex, appley
    
    # choose a pen color for the apple (15 is white on a black background;
    # you can pick another value if you like)
    display.set_pen(15)
    
    # draw a 5×5 block at the apple’s coordinates
    display.rectangle(applex + 5, appley + 5, 5, 5)

def checkapple():
    global score, snake

    # head-on-apple?
    if [applex, appley] in snake:
        score += 1
        snake.append(snake[-1][:])  # grow
        spawn_apple()               # new location immediately


def spawn_apple():
    global applex, appley

    while True:
        # pick a 5-pixel-aligned coord
        rx = random.randrange(0, 121, 5)
        ry = random.randrange(0,  56, 5)

        # make sure it doesn’t land on the snake
        if [rx, ry] not in snake:
            applex, appley = rx, ry
            break
def load_scores():

    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

def save_score(game_name, score):
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
    except (OSError, ValueError):
        scores = {}

    scores[game_name] = score

    temp_path = "scores.tmp"
    with open(temp_path, "w") as f:
        json.dump(scores, f)

    import uos
    uos.rename(temp_path, "scores.json")


def updatehighscore(score):
    if score > load_scores()["snake"]:
        save_score("snake", score)
    return

def reset():
    global gameover, snake, score, snakedir
    gameover = False
    snake = [[50, 50], [55, 50]]
    score = 0
    snakedir = "up"

spawn_apple()
while True:
    
    if gameover == False:
        print(score)
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        poll_and_print()
        drawsnake()
        movesnake()
        checkapple()
        
        drawapple()
        display.update()
        time.sleep(0.01)
        framestate = framestate * -1
    else:
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Game Over!", 20, 10)
        display.text("score:"+str(score), 20, 30)
        updatehighscore(score)
        display.text("highscore:"+str(load_scores()["snake"]), 10, 50)
        display.update()
        poll_and_print()


    
