import PCF8591 as ADC
import time

ADC.setup(0x48)
while True:
    ADC.write(0)
    time.sleep(0.1)
