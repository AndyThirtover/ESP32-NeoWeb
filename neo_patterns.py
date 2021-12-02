from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
from urandom import randint
import uasyncio as asyncio
import json

neo_pin = 14
LED_COUNT = 30
MAX = 255       # this is the maximum brightness
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
PURPLE = (128,0,128)
inv_speed = 254

config_json = {}
messages = []

def load_config():
    global LED_COUNT
    global MAX
    cf = open('config.json','r')
    config_json = json.load(cf)
    if config_json.get('LED_COUNT'):
        LED_COUNT = int(config_json['LED_COUNT'])
        print ("Current LED COUNT: {}".format(LED_COUNT))
    if config_json.get('MAX'):
        MAX = int(config_json['MAX'])
    cf.close()
    return config_json

config_json = load_config()  # Call this on startup
np = NeoPixel(Pin(neo_pin),LED_COUNT,bpp=3) # load after LED Count is known

def save_config(query):
    global config_json
    new_config = {}
    q_list = query.split('&')
    for pair in q_list:
        p_list = pair.split('=')
        new_config[p_list[0]] = p_list[1]
    print ("This config will be saved: {}".format(new_config))
    cf = open('config.json','w')
    json.dump(new_config,cf)
    cf.close()
    config_json = load_config() # reload



def scan(np, bounce_col):
    for i in range(LED_COUNT):
        prev = np[i]
        np[i] = bounce_col
        np.write()
        sleep_ms(inv_speed)
        np[i] = prev
        np.write()
    for i in reversed(range(LED_COUNT)):
        prev = np[i]
        np[i] =bounce_col
        np.write()
        sleep_ms(inv_speed)
        np[i] = prev
        np.write()

async def neo_off(np):
    for i in range(LED_COUNT):
        if np.bpp == 4:
            np[i] = (0,0,0,0)
        else:
            np[i] = (0,0,0)
    np.write()


def single_random(np):
    np[1] = (randint(0,255),randint(0,255),randint(0,128))
    np.write()




#---------------------------------------------------------------------------------------
#
#     Process Params and call functions
#
#---------------------------------------------------------------------------------------

async def random_pastel(np):
    rmin = const(2)
    rmax = const(128)
    gmax = const(64)
    bmax = const(32)
    wmax = const(16)
    for i in range(LED_COUNT):
        if np.bpp == 4:
            np[i] = (randint(rmin,rmax),randint(rmin,gmax),randint(0,bmax),randint(rmin,wmax))
        else:
            np[i] = (randint(rmin,rmax),randint(rmin,gmax),randint(0,bmax))
        np.write()

async def do_blend(np):
    current,target = extract_blend_colors()
    blend_to_end(np,current,target)

async def do_centre_static(np):
    current,target = extract_blend_colors()
    centre_static(np,current[0],current[1],current[2],current[3])

async def do_dim(np,level=50):
    for i in range(np.n):
        r,g,b,w = np[i]
        r = int(r*level/100)
        g = int(g*level/100)
        b = int(b*level/100)
        w = int(w*level/100)
        if np.bpp == 4:
            np[i] = (r,g,b,w)
        else:
            np[i] = (r,g,b)
        np.write()

async def do_scene(np,command):
    scene_def = command.split(':')[1].split('&')
    print ("Scene DEF: {}".format(scene_def))
    r = int(scene_def[0].split('=')[1])
    g = int(scene_def[1].split('=')[1])
    b = int(scene_def[2].split('=')[1])
    w = int(scene_def[3].split('=')[1])
    for i in range(np.n):
        if np.bpp == 4:
            np[i] = (r,g,b,w)
        else:
            np[i] = (r,g,b)
        np.write()


async def roll(np):
    while True:
        if len(messages):
            # There is something to do - do it
            command = messages.pop()
            print ("I got this command: {}".format(command))
            if 'random_pastel' in command:
                await random_pastel(np)
            elif 'neo_off' in command:
                await neo_off(np)
            elif 'blend' in command:
                await do_blend(np)
            elif 'centre' in command:
                await do_centre_static(np)
            elif 'dim' in command:
                await do_dim(np)
            elif 'static' in command:
                await do_scene(np,command)
            else:
                await asyncio.sleep_ms(200) 
        else:
            # sleep for a bit
            await asyncio.sleep_ms(50)


#---------------------------------------------------------------------------------------
#
#     BLEND and FADE functions.
#
#---------------------------------------------------------------------------------------

def extract_blend_colors():
    current = (int(config_json['CWRED']),int(config_json['CWGREEN']),int(config_json['CWBLUE']),int(config_json['CWWHITE']))
    target = (int(config_json['CWRED2']),int(config_json['CWGREEN2']),int(config_json['CWBLUE2']),int(config_json['CWWHITE2']))
    return current,target

def extract_ratio():
        return int(config_json['CWRATIO'])


def colour_floor(r,g,b,w,distance,ratio):
    fade = (ratio*1.0)/MAX
    return (light_floor(r*fade,distance,r),light_floor(g*fade,distance,g),light_floor(b*fade,distance,b),light_floor(w*fade,distance,w))


def light_floor(value,distance,max=MAX,shallow=True):
    if shallow :
        intensity = value - (distance*2)
    else:
        intensity = value - (distance*distance)
    if intensity < 0:
        return 0
    elif intensity > max:
        return max
    else:
        return int(intensity)

def centre_static(np,r,g,b,w):
    ratio = extract_ratio()
    for i in range ((np.n/2)+1):
        if int((np.n/2)+i) < np.n:
            np[int((np.n/2)+i)] = colour_floor(r,g,b,w,i,ratio)
        if int((np.n/2)-i) >= 0:
            np[int((np.n/2)-i)] = colour_floor(r,g,b,w,i,ratio)
        np.write()

def blend_int(c,t,step,steps):
    return int(c*(steps-step)/steps) + int(t*step/steps)

def blend_colour(current,target,step,steps):
    rc = current[0] 
    gc = current[1]
    bc = current[2]
    wc = current[3]
    rt = target[0]
    gt = target[1]
    bt = target[2]
    wt = target[3]
    return (
            blend_int(rc,rt,step,steps),
            blend_int(gc,gt,step,steps),
            blend_int(bc,bt,step,steps),
            blend_int(wc,wt,step,steps)
        )


def blend_pixel_value(np,i,left,right):
    return int((left*(np.n-i))/np.n) + int(right*i/np.n)
    #print("BV: {0}, LEFT:{1}, RIGHT{2}, INDEX{3}".format(bv,left,right,i))
    #return bv

def blend_to_end(np,left_colour, right_colour):
    rl = left_colour[0]
    gl = left_colour[1]
    bl = left_colour[2]
    wl = left_colour[3]
    rr = right_colour[0]
    gr = right_colour[1]
    br = right_colour[2]
    wr = right_colour[3]
    if np.bpp == 4:
        for i in range(np.n):
            np[i] = (
                    blend_pixel_value(np,i,rl,rr),
                    blend_pixel_value(np,i,gl,gr),
                    blend_pixel_value(np,i,bl,br),
                    blend_pixel_value(np,i,wl,wr))
            np.write()
    else:
        for i in range(np.n):
            np[i] = (
                    blend_pixel_value(np,i,rl,rr),
                    blend_pixel_value(np,i,gl,gr),
                    blend_pixel_value(np,i,bl,br))
            np.write()
