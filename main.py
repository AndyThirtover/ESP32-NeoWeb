try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import network
from microdot_asyncio import Microdot, Response
from web_gen import *
from neo_patterns import *
from watchd import *

# We need to know what address we are on.
wifi = network.WLAN(network.STA_IF)
print ("IP ADDRESS: {}".format(wifi.ifconfig()[0]))

async def main():
    await app.start_server(host='0.0.0.0', port=80, debug=True)
    print ("This is after the Web Server has started")


event_loop = asyncio.get_event_loop()

asyncio.create_task(main())
print ("CREATE TASK main - this starts the WebServer")

asyncio.create_task(monitor())
print ("CREATE TASK monitor - this is the watchdog")

asyncio.create_task(roll(np))
print ("CREATE TASK roll - this drives the NeoPixels")

event_loop.run_forever()