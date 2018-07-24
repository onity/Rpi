import RPi.GPIO as GPIO
import os
import time
import glob
from datetime import datetime

# Todo:
# output to SQL server rather than txt file.
# stream line
# add support for multiple buckets/Temp sensor.. Make bucketClass?
# add veg timer, though this could just be achieved by changing the on off times for flower

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)

outFile = 'TempLog.txt'
GPIO.setup(relayPin, GPIO.OUT)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#set file info
f = open(outFile,'a')
f.write('time, Temp, Fan On\n')
f.close()


# Constants
lightsOnHour = 22
lightsOutHour = 10
lightStatus = 0
currHour = 0
LIGHT_ON = 1
LIGHT_OFF = -1
LIGHT_ERR = 0
GPIO_LIGHT_PIN1 = 11
GPIO_LIGHT_PINT2 = 9
# set these pins
GPIO_LIGHT_FAN = 10

GPIO_RETURN_PIN1 = 2 
GPIO_RETURN_PIN2 = 1
GPIO_RETURN_FAN = 3
OFF = 1
ON = 0
FLOWER_MODE = 1

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c


def recordTemp(tempC):
	#used to record the current temp
	print str(datetime.now()) +' temp: '+str(tempC)
	f = open(outFile,'a')
	f.write(str( datetime.now()) + ', ' + str(tempC) + 'c, '+ str(GPIO.input(GPIO_RETURN_PIN1))+ ', '+ str(GPIO.input(GPIO_RETURN_PIN1)) +'\n')
	f.close()

def checkTemp():
	#used to check the temperature and change the lights/fan
	# ToDo: add switching of lights to give more even finish
	#	Control the fan

	tempC = read_temp()
	
	if tempC <= 23.0 and GPIO.input(GPIO_RETURN_FAN) == OUT:
		GPIO.output(GPIO_LIGHT_FAN, IN)

	elif tempC > 25.0 and GPIO.input(GPIO_RETURN_FAN) != OUT:
		GPIO.output(GPIO_LIGHT_FAN, OUT)
	
	if tempC <= 22.0 and GPIO.input(GPIO_RETURN_PIN2) != ON:
                GPIO.output(GPIO_LIGHT_PIN1, ON)
		GPIO.output(GPIO_LIGHT_PIN2, ON)
                
        if tempC > 26.0 and GPIO.input(GPIO_RETURN_PIN2) != OFF:
		GPIO.output(GPIO_LIGHT_PIN2, OFF)
                
	recordTemp(tempC)

def changeLights( successVal):
	if successVal == LIGHT_ON:
		#write GPIO to turn all Lights on, checkTemp() will controls lights on or off
		GPIO.output(GPIO_LIGHT_PIN1, ON)
		GPIO.output(GPIO_LIGHT_PIN2, ON)
		return LIGHT_ON

	elif successVal == LIGHT_OFF:
                #writeGPIO to turn all Lights off
		GPIO.output(GPIO_LIGHT_PIN1, OFF)
                GPIO.output(GPIO_LIGHT_PIN2, OFF)
		return LIGHT_OFF

	else:
		#error
		return LIGHT_ERR
		

try:
	while True:
		currHour = datetime.now().time().hour
		if (currHour >= lightsOnHour or currHour < lightsOutHour) or FLOWER_MODE == 0:
			if lightStatus < LIGHT_ON:
				lightStatus = changeLights( LIGHT_ON)
			checkTemp()
		
		else:
			if lightStatus > LIGHT_OFF:
				lightStatus = changeLights( LIGHT_OFF)
			recordTemp(read_temp())
	#only trigger every minute, could be left out for spam...
	time.sleep(60)

except KeyboardInterrupt:
        GPIO.cleanup()
        print 'GPIOCleaned'

except Exception as e:
        print 'err2: '+ str(e)
        GPIO.cleanup()
        print 'GPIOCleaned'
else:
        GPIO.cleanup()
        print 'GPIOCleaned'




