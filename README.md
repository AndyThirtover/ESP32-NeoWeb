# ESP32-NeoWeb
Micropython ESP32 Neopixels Driver for RGBW leds with builtin Web Server

The webserver comes from the Microdot project

Tested with MicroPython 1.17

You'll need to add a boot.py to connect to WLAN/LAN

Connections:

	IO14 - Data to NeoPixels
	IO16 - Push Button 0
	IO17 - Push Button 1

Known Issues

Web page is slow to serve on poor Wifi connections.

Calling the web page during a long NeoPixel operation will time out.