#!/usr/bin/env python2.7
from __future__ import division
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import numpy as np
from numpy.polynomial import Polynomial as P
from numpy import matrix

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# Define variables as lists of zeros, we will log 10 measurements
scale_factor=10
waterlevel_reads=[0]*scale_factor
ref_sig=[0]*scale_factor


# Loop through 10 measurments and save in a list
for i in range(0,scale_factor):
        waterlevel_reads[i] = mcp.read_adc(1)
        ref_sig[i] = mcp.read_adc(0)
        time.sleep(.1)


normalized_read = matrix(waterlevel_reads)/matrix(ref_sig) # divide the list of water levels by the corresponding reference signal at each measurement

print(np.mean(normalized_read))

#################################################
### Use this format to validate your equation ###
#################################################
#known_value = 0.753 # insert a sensor output logged for a known value in inches that wasn't used in the standard curve, I put in a random number here
## Regression inputs
### These were the output for calibrating my sensor
#x = [0,3,4,5,6.5,7,8,9,10,11,12,0,1,2.5,3,4,6,7,8,9,10,11,12]
#y = [1.0,0.971621622,0.948787062,0.915775401,0.869318182,0.843537415,0.805107527,0.751978892,0.692307692,0.608870968,0.541490858,1.013661202,
#1.016460905,0.986282579,0.971193416,0.94109589,0.879286694,0.845205479,0.802469136,0.747599451,0.696844993,0.617283951,0.541838134]
#p = P.fit(x ,y ,2) # create second order polynomial, the r^2 was 0.9998 and I validated my equation outputs
#sensor_inches=(p - known.value).roots()[1] # use the average validation value you logged for water level measurement to calculate inches of water the sensor is detecting
#### You're validating the equation here by plugging in an average sensor output value for a known measurments of volumes and making sure it predicts the correct value in inches


