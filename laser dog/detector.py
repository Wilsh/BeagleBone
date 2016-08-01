#!/usr/bin/python 
'''Author: Andrew Seligman 
Date: 6.8.16 
This program uses a BeagleBone Black to track the outdoor habits of my dog. 
There are three LED lights to be placed indoors and an infrared-based proximity 
sensor to be placed just outside the door. A physical switch activates a circuit 
when she first goes outside, which will light the green LED. After a short 
period of time (determined by yellowSeconds), the yellow LED will light up. 
Because she will wait by the door when she is ready to come in, the 
proximity sensor will light the red LED upon detecting her prescence. In case the 
original switch is prematurely toggled off, there is a grace period during which the 
timer for the yellow LED is preserved. Future updates will integrate networking code 
to send these actions to my PC
'''

import Adafruit_BBIO.GPIO as GPIO
import time

#begin LED sequence and collect IR sensor input 
#yellowSeconds are seconds after which to turn on yellow LED
def activated(yellowSeconds):
	yellowOff = 1
	baseTime = time.time()
	GPIO.output(greenLED, GPIO.HIGH)
	if yellowSeconds == 60*10:
		print getTime() + "Ammy is going out"
	while GPIO.input(actCircuit): 
		timePassed = time.time() - baseTime
		if yellowOff and (timePassed > yellowSeconds):
			yellowOff = 0
			GPIO.output(yellowLED, GPIO.HIGH)
			print getTime() + "Ammy has been out for 10 minutes"
		#IR sensor drops to 0V when activated
		if GPIO.input(irSensor):
			GPIO.output(redLED, GPIO.LOW)
		else:
			GPIO.output(redLED, GPIO.HIGH)
			if timePassed > 20:
				print getTime() + "Ammy is waiting to come in"
		time.sleep(1)
	return int(time.time() - baseTime)

#system deactivated; turn off LEDs
def standby():
	GPIO.output(redLED, GPIO.LOW)
	GPIO.output(yellowLED, GPIO.LOW)
	GPIO.output(greenLED, GPIO.LOW)

#return time as formatted string "day hr:min:sec "
def getTime():
	return time.strftime("%a %H:%M:%S ", time.localtime())

redLED = "P8_11"
yellowLED = "P8_12"
greenLED = "P8_13"
irSensor = "P8_14"
actCircuit = "P8_15"

GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(yellowLED, GPIO.OUT)
GPIO.setup(greenLED, GPIO.OUT)
GPIO.setup(irSensor, GPIO.IN)
GPIO.setup(actCircuit, GPIO.IN)

try:
	print "Laser Dog System activated"
	recentlyActivated = 0
	elapsedTime = 0
	resetCounter = 20
	while True:
		if GPIO.input(actCircuit):
			elapsedTime = activated(60*10 - elapsedTime)
			standby()
			recentlyActivated = 1
		if recentlyActivated:
			if resetCounter > 0:
				resetCounter -= 1
			else:
				recentlyActivated = 0
				elapsedTime = 0
				resetCounter = 20
				print getTime() + "Ammy is in"
		time.sleep(1)
finally:
	GPIO.cleanup()
