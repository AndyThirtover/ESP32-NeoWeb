from machine import WDT, reset
import uasyncio as asyncio
import network

"""
   WATCHDOG -- Reboot system if Network not seen for 600 seconds
   or any other system crash
"""

mon_period = const(600000)
dog_period = const(600000+1000)

wdt = WDT(timeout=dog_period)
wifi = network.WLAN(network.STA_IF)


async def monitor():
	while True:
		wdt.feed()
		await asyncio.sleep_ms(mon_period) #  wait for longer than watchdog to force a reboot
		if not wifi.isconnected():
			print("WiFi: {}".format(wifi.isconnected()))
			reset() #  cause a reboot of the system to provoke a wifi reconnect
