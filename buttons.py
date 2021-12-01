from machine import Pin
from utime import sleep_ms
from urandom import randint
from neo_patterns import *
import uasyncio as asyncio
import json

debounce = const(10)

async def buttons():
	off_pin = Pin(16, Pin.IN, Pin.PULL_UP)
	off_count = 0
	scene_pin = Pin(17, Pin.IN, Pin.PULL_UP)
	scene_count = 0

	while True:
		#print ("OFF Pin: {}".format(off_pin.value()))
		#print ("SCENE Pin: {}".format(scene_pin.value()))
		if not off_pin.value():
			off_count += 1
		if not scene_pin.value():
			scene_count += 1
		if off_count > debounce:
			messages.append("neo_off")
			off_count = 0
			#print("neo_off from button")
		if scene_count > debounce:
			messages.append("blend")
			scene_count = 0
			#print("blend from button")

		await asyncio.sleep_ms(50)