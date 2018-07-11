import RPi.GPIO as GPIO
import os
import time
import glob
from datetime import datetime

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)

relayPin = 9
fanOn = 0
outFile = 'TempLog.txt'
GPIO.setup(relayPin, GPIO.OUT)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#set file info
f = open(outFile,'a')
f.write('time, Temp, Fan On\n')
f.close()


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

def fan_control(tempC):
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(relayPin, GPIO.OUT)
        if tempC <= 23.0 and fanOn != 1:
                GPIO.output(relayPin, 0)
                return 1
        if tempC > 25.0 and fanOn != 0:
                GPIO.output(relayPin, 1)
                return 0
        return fanOn

try:
        while True:
                tempC = read_temp()
                fanOn = fan_control(tempC)
                print str(datetime.now()) +' temp: '+str(tempC)
                f = open(outFile,'a')
                f.write(str( datetime.now()) + ', ' + str(tempC) + 'c, '+ str(fanOn)+'\n')
                f.close()
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
