#!/usr/bin/python 
'''Author: Andrew Seligman 
Date: 10.3.18 
This program uses a BeagleBone Black to track the outdoor habits of my dog. 
There are three LED lights to be placed indoors and an infrared-based proximity 
sensor to be placed just outside the door. A physical switch activates a circuit 
when she first goes outside, which will light the green LED. After a short 
period of time (determined by WARNTIME), the yellow LED will light up. 
Because she will wait by the door when she is ready to come in, the 
proximity sensor will light the red LED upon detecting her prescence. In case the 
original switch is prematurely toggled off, there is a grace period during which the 
timer for the yellow LED is preserved.

This version of the program acts as a network server to allow other computers on
the LAN to obtain a simplified status of the program. The client will expect to
receive one of four responses:
    'white' - the program is running and the activation circuit is off
    'green' - the activation circuit is on
    'yellow' - the activation circuit has been on for at least WARNTIME seconds
    'red' - the proximity sensor is being activated
'''

import Adafruit_BBIO.GPIO as GPIO
import time, socket, threading

HOST = '10.0.0.8'
PORT = 24680
LED_status = "white"

WARNTIME = 60*15

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

class AcceptClients(threading.Thread):
    '''Create a new thread to accept incoming client connections
    '''
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            client, addr = s.accept()
            HandleClient(client, addr).start()

class HandleClient(threading.Thread):
    '''Create a new thread to handle the given client connection
    '''
    def __init__(self, client, addr):
        self.client = client
        self.addr = addr
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            try:
                self.client.sendall(LED_status.encode('utf-8'))
                time.sleep(1)
                self.data = self.client.recv(1024)
                if not self.data:
                    break
            except ConnectionResetError:
                print("ConnectionResetError")
                break
            except BrokenPipeError:
                print("BrokenPipeError")
                break
        self.client.close()

#begin LED sequence and collect IR sensor input 
#yellowSeconds are seconds after which to turn on yellow LED
def activated(yellowSeconds):
	yellowOff = True
	baseTime = time.time()
	GPIO.output(greenLED, GPIO.HIGH)
	if yellowSeconds == WARNTIME:
		print getTime() + "Ammy is going out"
	while GPIO.input(actCircuit): 
		timePassed = time.time() - baseTime
		if yellowOff and (timePassed > yellowSeconds):
			yellowOff = False
			GPIO.output(yellowLED, GPIO.HIGH)
			print getTime() + "Ammy has been out for " + str(WARNTIME/60) + " minutes"
        
		#IR sensor drops to 0V when activated
		if GPIO.input(irSensor):
			GPIO.output(redLED, GPIO.LOW)
		else:
			GPIO.output(redLED, GPIO.HIGH)
            #opening the door triggers the proximity sensor, so wait a bit
			if timePassed > 20:
				print getTime() + "Ammy is waiting to come in"
        
        #determine color to send over network
        if not GPIO.input(irSensor) and timePassed > 20:
            #red LED takes precedence
            LED_status = "red"
        elif timePassed > yellowSeconds:
            LED_status = "yellow"
        else:
            LED_status = "green"
        
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

try:
    AcceptClients().start()
	print "Laser Dog System activated"
	recentlyActivated = False
	elapsedTime = 0
	resetCounter = 20
	while True:
		if GPIO.input(actCircuit):
			elapsedTime = activated(WARNTIME - elapsedTime)
			standby()
			recentlyActivated = True
		if recentlyActivated:
			if resetCounter > 0:
				resetCounter -= 1
			else:
				recentlyActivated = False
				elapsedTime = 0
				resetCounter = 20
				print getTime() + "Ammy is in"
                LED_status = "white"
		time.sleep(1)
finally:
	GPIO.cleanup()
