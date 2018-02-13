from socketIO_client_nexus import SocketIO, LoggingNamespace
import time
from random import *

# Simple heart beat reader for Raspberry pi using ADS1x15 family of ADCs and a pulse sensor - http://pulsesensor.com/.
# The code borrows heavily from Tony DiCola's examples of using ADS1x15 with 
# Raspberry pi and WorldFamousElectronics's code for PulseSensor_Amped_Arduino

# Author: Udayan Kumar
# License: Public Domain

import time
import PCF8591 as ADC


if __name__ == '__main__':
    ADC.setup(0x48) #TODO: Select the correct ADC channel. I have selected A0 here
    # initializaadction 
    GAIN = 2/3  
    curState = 0
    threshSetting = 560
    thresh = threshSetting  # mid point in the waveform
    P = 512
    T = 512
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100

    lastTime = int(time.time()*1000)
    with SocketIO('13.125.124.80', 3000, LoggingNamespace) as socketIO:
        # Main loop. use Ctrl-c to stop the code
        while True:
            # read from the ADC
            Signal = int(ADC.read(0))*4
	    # print "signal: " + str(Signal)
            ADC.write(0)
            curTime = int(time.time()*1000)

            sampleCounter += curTime - lastTime;      #                   # keep track of the time in mS with this variable
            lastTime = curTime
            N = sampleCounter - lastBeatTime;     #  # monitor the time since the last beat to avoid noise
            #print N, Signal, curTime, sampleCounter, lastBeatTime

            ##  find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3.0 :  #       # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T :                        # T is the trough
                    T = Signal;                         # keep track of lowest point in pulse wave 

            if Signal > thresh and  Signal > P:           # thresh condition helps avoid noise
                P = Signal;                             # P is the peak
                                                    # keep track of highest point in pulse wave

            #  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
            # signal surges up in value every time there is a pulse
            if N > 250 :                                   # avoid high frequency noise
                if  (Signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
                    Pulse = True;                               # set the Pulse flag when we think there is a pulse
                    IBI = sampleCounter - lastBeatTime;         # measure time between beats in mS
                    lastBeatTime = sampleCounter;               # keep track of time for next pulse

                if secondBeat :                        # if this is the second beat, if secondBeat == TRUE
                    secondBeat = False;                  # clear secondBeat flag
                    for i in range(0,10):             # seed the running total to get a realisitic BPM at startup
                        rate[i] = IBI;                      

                if firstBeat :                        # if it's the first time we found a beat, if firstBeat == TRUE
                    firstBeat = False;                   # clear firstBeat flag
                    secondBeat = True;                   # set the second beat flag
                    continue                              # IBI value is unreliable so discard it


                # keep a running total of the last 10 IBI values
                runningTotal = 0;                  # clear the runningTotal variable    

                for i in range(0,9):                # shift data in the rate array
                    rate[i] = rate[i+1];                  # and drop the oldest IBI value 
                    runningTotal += rate[i];              # add up the 9 oldest IBI values

                rate[9] = IBI;                          # add the latest IBI to the rate array
                runningTotal += rate[9];                # add the latest IBI to runningTotal
                runningTotal /= 10;                     # average the last 10 IBI values 
                BPM = 60000/runningTotal;               # how many beats can fit into a minute? that's BPM!
                if BPM < 150: # remove noise
                    print 'BPM: {}'.format(BPM)
                    socketIO.emit('heartbeat',str(BPM)) # Send To Socket IO
		else:
		   socketIO.emit('heartbeat', str(0))

            if Signal < thresh and Pulse == True :   # when the values are going down, the beat is over
		print "over"
                Pulse = False;                         # reset the Pulse flag so we can do it again
                amp = P - T;                           # get amplitude of the pulse wave
                thresh = amp/2 + T;                    # set thresh at 50% of the amplitude
                P = thresh;                            # reset these for next time
                T = thresh;

            if N > 2500 :                          # if 2.5 seconds go by without a beat
		print "without"
                thresh = threshSetting;                          # set thresh default
                P = 512;                               # set P default
                T = 512;                               # set T default
		sampleCounter = 0;
		lastBeatTime = 0;
                firstBeat = True;                      # set these to avoid noise
                secondBeat = False;                    # when we get the heartbeat back
		Pulse = False;
		IBI = 600
		rate = [0]*10
		amp = 100
                print "no beats found"
		socketIO.emit('heartbeat', str(0))

            time.sleep(0.1)
