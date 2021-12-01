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
print ("Status: {}".format(wifi.ifconfig()))

async def main():
    await app.start_server(host='0.0.0.0', port=80, debug=True)
    print ("This is after the Web Server has started")


event_loop = asyncio.get_event_loop()

asyncio.create_task(main())
print ("This is after the asyncio create_task of main")

asyncio.create_task(monitor())
print ("This is after the asyncio create_task of monitor - the watchdog thread")

asyncio.create_task(roll(np))
print ("This is after the asyncio create_task of roll")

event_loop.run_forever()