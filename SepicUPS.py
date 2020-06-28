# Copyright Nigel Brooke 12/8/2017 
import os
import curses
import time
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
global VIN
global BattVoltage
#BatteryThreshold sets the voltage at which the raspberry pi will go into shutdown for NiMH cells it is recommended
#to set this to 1.0V per cell
 
BatteryThreshold = 4.9
Total = 0
Average = 100
InputVoltge = 0
NosofSamples = 10
VIN_adc=1
BATT_adc=0
InputLED = 21
BattLED = 22
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 17
VIN=0
BattVoltage= 0
# set up the SPI interface pins
GPIO.setwarnings(False)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
# set up the LED's
GPIO.setup(InputLED,GPIO.OUT)
GPIO.setup(BattLED,GPIO.OUT)

Logtofile = 0

def cls():
	os.system('clear')

# read SPI data from MCP3002 chip,
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 1) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
        if adcnum == 0 :
			commandout = 0x18 # start bit + single-ended bit
			commandout <<= 3    # we only need to send 5 bits here
        if adcnum == 1 :
			commandout = 0x1C
			commandout <<= 3
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
				

def Window():
	variable = 6
	stdscr = curses.initscr()
	begin_x = 20; begin_y = 7
	height = 3; width = 15
	win = curses.newwin(height, width, begin_y, begin_x)
	stdscr.addstr(2,1, " Raspberry Pi UPS",curses.A_BOLD)

	stdscr.addstr(4, 2, "Input   Voltage   : ")
	stdscr.addstr(5, 2, "Battery Voltage   : ")
	stdscr.addstr(6, 2, "Battery Threshold : ")
	stdscr.addstr(7, 2,  "Power Status      : ")
	stdscr.addstr(6, 23,str(BatteryThreshold),curses.A_BOLD)
	stdscr.addstr(4, 23,str(VIN),curses.A_BOLD)
	stdscr.addstr(5, 23,str(BattVoltage),curses.A_BOLD)
	if (VIN>BattVoltage):
			stdscr.addstr(7, 23,"OK    ",curses.A_BOLD)
	else:
			stdscr.addstr(7, 23,"BACKUP",curses.A_BOLD)
	if (BattVoltage<BatteryThreshold):
			stdscr.addstr(7, 23,"SHUTDOWN",curses.A_BOLD)
			stdscr.refresh()
			time.sleep(30)
			if (BattVoltage<BatteryThreshold):
				GPIO.cleanup()
				os.system('sudo halt')
	stdscr.refresh()
		
				
count = 0
cls()


while True:

		# read the analog pin
		for i in range(Average):
			VIN = readadc(BATT_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
			VIN = ((VIN*33.0)/4096)
			Total = Total + VIN
		VIN =round(Total/Average,1)
		Total=0
		for i in range(Average):
			BattVoltage = readadc(VIN_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
			BattVoltage = ((BattVoltage*33.0)/4096)
			Total = Total + BattVoltage
		BattVoltage =round(Total/Average,1)
		Total=0
		if VIN >= 4:
			GPIO.output(InputLED, GPIO.LOW)
		else:
			GPIO.output(InputLED, GPIO.HIGH)
			
		if BattVoltage >= 4:
				GPIO.output(BattLED, GPIO.LOW)
		else:
				GPIO.output(BattLED, GPIO.HIGH)
		
		# how much has it changed since the last read?
		# hang out and do nothing for a half second
		Window()
		time.sleep(1)


#Shutdown()
	
