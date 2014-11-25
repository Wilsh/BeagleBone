#!/usr/bin/python
#Author: Andrew Seligman
#Date: 11.4.14
#This program uses the system time to control LEDs that function as 
#a binary clock using a BeagleBone Black

import Adafruit_BBIO.GPIO as GPIO
from time import localtime, strftime, sleep

#return the system time as a tuple in hours, minutes, and seconds
def getTime():
	time = localtime()
	hour = int(strftime("%H", time))
	minute = int(strftime("%M", time))
	second = int(strftime("%S", time))
	#ignore leap seconds
	if(second > 59):
		second = 59
	return (hour, minute, second)

#display the time for given hour, minute, and second parameters
def displayTime(h, m, s):
	toggleLED(h, "hour", 0)
	toggleLED(m, "minute", 1)
	toggleLED(s, "second", 2)

#light hour, minute, or second LEDs based on given value
def toggleLED(value, name, index):
	if(name == "hour"):
		limit = 5
		base = 16
	else:
		limit = 6
		base = 32

	for idx in reversed(range(0,limit)):
		if(value/base > 0):
			GPIO.output(pins[index][idx], GPIO.HIGH)
			value -= base
		else:
			GPIO.output(pins[index][idx], GPIO.LOW)
		base /= 2

secondPins = ("P8_11","P8_12","P8_13","P8_14","P8_15","P8_16")
minutePins = ("P8_17","P8_18","P8_19","P9_14","P9_15","P9_16")
hourPins = ("P9_23","P9_27","P9_30","P9_41","P9_42")
pins = (hourPins, minutePins, secondPins)

for idx in range(0,3):
    for pin in pins[idx]:
        GPIO.setup(pin, GPIO.OUT)

time = getTime()
hour = time[0]
minute = time[1]
second = time[2]

try:
	while True:
		displayTime(hour, minute, second)
		#resync time each hour
		if(minute == 59 and second == 59):
			time = getTime()
			hour =  time[0]
			minute = time[1]
			second = time[2]
		if(second < 59):
			second += 1
		else:
			second = 0
			if(minute < 59):
				minute += 1
			else:
				minute = 0
				if(hour < 23):
					hour += 1
				else:
					hour = 0
		sleep(0.9921)
finally:
	GPIO.cleanup()
