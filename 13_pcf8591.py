#!/usr/bin/env python
import PCF8591 as ADC
from time import sleep

Treshold = 550
beat = 0

def setup():
	ADC.setup(0x48)

def loop():
	while True:
		signal = int(ADC.read(0))*4
		if signal > Treshold:
			print signal
		ADC.write(ADC.read(0))
		sleep(0.01)

def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()
