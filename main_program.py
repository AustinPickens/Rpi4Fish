#!/usr/bin/env python2.7
from __future__ import division
import json, os, glob, time, requests
from datetime import datetime
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import numpy as np
from numpy.polynomial import Polynomial as P
from numpy import matrix

credentials_in=open(os.getcwd() +'/Rpi4Fish/master_data.json')
credentials=json.load(credentials_in)
last_data_log_in=open(os.getcwd() +'/Rpi4Fish/Data_from_sensors.json')
last_data_log=json.load(last_data_log_in)


############################
### Define Pin Locations ###
############################

## For ADC
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


################################
###  Temperature Sensor Code ###
################################

## Read Temperature
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

## Access bus devices
base_dir = '/sys/bus/w1/devices/'
tank_folder= glob.glob(base_dir + credentials['Temp_sensors']['tank_bus'])[0]
tank_file = tank_folder + '/w1_slave'
ambient_folder = glob.glob(base_dir + credentials['Temp_sensors']['ambient_bus'])[0]
ambient_file = ambient_folder + '/w1_slave'

## Define temperature function
def tank_raw():
    f = open(tank_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def ambient_raw():
    f = open(ambient_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def tank_temp():
    lines = tank_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

def ambient_temp():
    lines = ambient_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


#############################################################
### Water level, leak sensors, light sensor, temp sensors ###
#############################################################

# Define variables as lists of zeros, we will log 10 measurements
# If you don't have an ADC
number_of_measurments=10
light_reads=[0]*number_of_measurments
waterlevel_reads=[0]*number_of_measurments
leaksens1_reads=[0]*number_of_measurments
leaksens2_reads=[0]*number_of_measurments
ambient_temp_reads=[0]*number_of_measurments
tank_temp_reads=[0]*number_of_measurments
ref_sig=[0]*number_of_measurments

if(credentials['ADC_presets']['active']!=False and credentials['Temp_sensors']['active']!=False):
    # Loop through 20 measurments and save in a list
    for i in range(0,number_of_measurments):
        light_reads[i] = mcp.read_adc(credentials['ADC_presets']['light_sensor'])/1023
        waterlevel_reads[i] = mcp.read_adc(credentials['ADC_presets']['water_level_sensor']['adc_pin'])
        ref_sig[i] = mcp.read_adc(credentials['ADC_presets']['reference_signal'])
        leaksens1_reads[i] = mcp.read_adc(credentials['ADC_presets']['leak sensors']['sensor_1'])/1023
        leaksens2_reads[i] = mcp.read_adc(credentials['ADC_presets']['leak sensors']['sensor_2'])/1023
        ambient_temp_reads[i]=ambient_temp()
        tank_temp_reads[i]=tank_temp()
        time.sleep(.1)
elif(credentials['ADC_presets']['active']!=False and credentials['Temp_sensors']['active']!=True):
    # If you have ADC and not temp sensors
    for i in range(0,number_of_measurments):
        light_reads[i] = mcp.read_adc(credentials['ADC_presets']['light_sensor'])/1023
        waterlevel_reads[i] = mcp.read_adc(credentials['ADC_presets']['water_level_sensor']['adc_pin'])
        ref_sig[i] = mcp.read_adc(credentials['ADC_presets']['reference_signal'])
        leaksens1_reads[i] = mcp.read_adc(credentials['ADC_presets']['leak sensors']['sensor_1'])/1023
        leaksens2_reads[i] = mcp.read_adc(credentials['ADC_presets']['leak sensors']['sensor_2'])/1023
        time.sleep(.1)
elif(credentials['ADC_presets']['active']!=True and credentials['Temp_sensors']['active']!=False):
    # Loop through 20 measurments and save in a list
    for i in range(0,number_of_measurments):
        waterlevel_reads[i] = mcp.read_adc(credentials['ADC_presets']['water_level_sensor']['adc_pin'])
        ref_sig[i] = mcp.read_adc(credentials['ADC_presets']['reference_signal'])
        ambient_temp_reads[i]=ambient_temp()
        tank_temp_reads[i]=tank_temp()
        time.sleep(.1)


## Regression inputs
if(credentials['ADC_presets']['water_level_sensor']['active']!=False):
    normalized_read = matrix(waterlevel_reads)/matrix(ref_sig) # divide the list of water levels by the corresponding reference signal at each measurement
    x=credentials['Tank_Info']["regression_inputs"]['x']
    y=credentials['Tank_Info']["regression_inputs"]['y']
    p = P.fit(x ,y ,2) # create second order polynomial, the r^2 was 0.9998 and I validated my equation outputs
    sensor_inches=(p - np.mean(normalized_read)).roots()[1] # use the average normalized water level measurement to calculate inches of water the sensor is detecting
    #### I validated this equation performed best by plugging in known measurments for volumes 
    ## My tank is rectangular, therefore, length*width*height = volume in^3
    l=credentials['Tank_Info']['rectangular_tank']['length'] # length in inches
    w=credentials['Tank_Info']['rectangular_tank']['width']  # width in inches
    h=credentials['Tank_Info']['rectangular_tank']['height_until_full']-(12.5-sensor_inches) # the max water sensor mark is exactly 22 inches from bottom of tank, so subtract 22 inches from current water level reading minus 12.5
    current_volume=(l*w*h)/230.9993 # Calculates current volume in tank, based on sensor reading. 1 gal = 230.9993 in^3
    total_volume=(l*w*credentials['Tank_Info']['rectangular_tank']['height_until_full'])/230.9993 # calculates total volume of tank
    water_level_data = current_volume/total_volume  # tank is 35 gallons to a safe fill level

#########################
### Weather Simulator ###
#########################
## Define Weather Simulator Function
def weather_simulator():
        if(credentials['Weather_simulation']['active']!=False):
            if prim_cond == "Rain":
                    if(credentials['Weather_simulation']['Rain']!=False):
                        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Rain'])
            elif prim_cond == "Thunderstorm":
                    if(credentials['Weather_simulation']['Thunderstorm']!=False):
                        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Thunderstorm'])
            elif prim_cond == 'Drizzle':
                    if(credentials['Weather_simulation']['Drizzle']!=False):
                        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Drizzle'])
            elif prim_cond == "Clear":
                    if(credentials['Weather_simulation']['Clear']!=False):
                        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Clear'])
            elif prim_cond == "Clouds":
                    if sec_cond == "few clouds":
                            if(credentials['Weather_simulation']['few clouds']!=False):
                                os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['few clouds'])
                    elif sec_cond == "scattered clouds":
                            if(credentials['Weather_simulation']['scattered clouds']!=False):
                                os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['scattered clouds'])
                    elif sec_cond == "broken clouds":
                            if(credentials['Weather_simulation']['broken clouds']!=False):
                                os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['broken clouds'])
                    elif sec_cond == "overcast clouds":
                            if(credentials['Weather_simulation']['overcast clouds']!=False):
                                os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['overcast clouds'])
                    else:
                            if(credentials['Weather_simulation']['default_clouds']!=False):
                                os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['default_clouds'])
            else:
                    if(credentials['Weather_simulation']['default']!=False):
                        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['default'])

## Hit the Weather API
r = requests.get(url=credentials['Weather']['api'])
conditions = r.json()['weather'][0]
prim_cond = conditions['main']
sec_cond = conditions['description']

## Logic conditions for time of day and weather
if(credentials['Weather_simulation']['active']!=False):
    cur_time=datetime.now().strftime('%H:%M') # get current date and time to prevent changing light during light cycle on and off
    if "07:30" <= cur_time <= "16:55":
            if "07:30" <= cur_time <= "8:00": # this code chunk changes the light, after light on sequence, to the current weather
                    weather_simulator()
            elif conditions !=last_data_log['Conditions']: # if the weather has not changed, the light is left on the current setting
                    weather_simulator()


## Data to save
# This area should run okay if you are missing some combination of project, it should still push data to you Firebase database
if(credentials['ADC_presets']['active']!=False and credentials['Temp_sensors']['active']!=False and credentials['ADC_presets']['water_level_sensor']['active']!=False):
    # You have all sensors
    data_out = {'Values':{"Time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Tank Temp":np.mean(tank_temp_reads), "Ambient Temp": np.mean(ambient_temp_reads), "Light": np.mean(light_reads), "Water": water_level_data, "Leak1":np.mean(leaksens1_reads), "Leak2": np.mean(leaksens2_reads)}, "Conditions": conditions}
elif(credentials['ADC_presets']['active']!=True and credentials['Temp_sensors']['active']!=False):
    # You are missing ADC sensors
    data_out = {'Values':{"Time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Tank Temp":np.mean(tank_temp_reads), "Ambient Temp": np.mean(ambient_temp_reads), "Light": 0, "Water": 0, "Leak1":0, "Leak2":0}, "Conditions": conditions}
elif(credentials['ADC_presets']['active']!=False and credentials['Temp_sensors']['active']!=True and credentials['ADC_presets']['water_level_sensor']['active']!=False):
    data_out = {'Values':{"Time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Tank Temp":0, "Ambient Temp":0, "Light": 0, "Water": water_level_data, "Leak1":0, "Leak2": 0}, "Conditions": conditions}
elif(credentials['ADC_presets']['active']!=False and credentials['Temp_sensors']['active']!=False and credentials['ADC_presets']['water_level_sensor']['active']!=True):
    data_out = {'Values':{"Time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Tank Temp":np.mean(tank_temp_reads), "Ambient Temp": np.mean(ambient_temp_reads), "Light": np.mean(light_reads), "Water": 0, "Leak1":np.mean(leaksens1_reads), "Leak2": np.mean(leaksens2_reads)}, "Conditions": conditions}
else:
    data_out = {'Values':{"Time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Tank Temp": 0, "Ambient Temp": 0, "Light": 0, "Water": 0, "Leak1": 0, "Leak2": 0}, "Conditions": conditions}

## Open and save file
with open('Data_from_sensors.json', 'w') as fp:
    json.dump(data_out, fp)

