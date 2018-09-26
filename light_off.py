#!/usr/bin/env python3.4
import os, time, json

credentials_in=open(os.getcwd() +'/Rpi4Fish/master_data.json')
credentials=json.load(credentials_in)

if(credentials['Weather_simulation']['Sunrise_set']!=False):
        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Sunrise_set'])
        time.sleep(600)

if(credentials['Weather_simulation']['Moon_light']!=False):
        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Moon_light'])
        time.sleep(300)

if(credentials['Weather_simulation']['Moon_dark']!=False):
        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Moon_dark'])
        time.sleep(300)

if(credentials['Weather_simulation']['Moon_darkest']!=False):
        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Moon_darkest'])
        time.sleep(600)

if(credentials['Weather_simulation']['Power']!=False):
        os.system("irsend SEND_ONCE" + " " + os.getcwd() + "/" + credentials['Weather_simulation']['LIRC_file'] + " " + credentials['Weather_simulation']['Power'])

