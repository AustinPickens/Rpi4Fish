# Rpi4Fish
Automated Fish Tank System Using Raspberry Pi, Python, and R Shinny for Graphic User Interface.

## Background
Rpi4Fish is an open source project developed to control and monitor your fish tank, however, the core functionality can easily be modified for many other applications. The inspiration for this project started when I purchased a fish tank light that can simulate weather conditions using an infrared remote, I thought to myself "it would be so cool if a computer could check the weather report, then change the light in by emitting the same infrared signal as the remote". Rpi4Fish utilizes the microcontroller raspberry pi (i.e., Raspberry Pi Zero W) to execute scripts written in the programming language Python, which log data from sensors configured to the Raspberry Pi. The data is then pushed to a cloud NoSQL database. Finally, using R Shiny, the data is pulled into a graphic user interface (GUI) that displays all the data at https://Rpi4Fish.com. You can download R and run the website locally using data generated from my fish tank, so you do not need any of the hardware to get something from the project. You can host the application through https://www.shinyapps.io, and you get 25 hours of free service a month -OR- you can host your own cloud server and website like I did for https://Rpi4Fish.com .

I rewrote all the source code in such a way where someone with no experience could walk through and understand what is happening. 

## Hardware Instructions

## Setting the Raspberry Pi

### Setting up the Operating System (OS) and SSH
If you are using the Raspberry Pi Zero, you'll need to configure it so it can connect to your internet and you can ssh into it. SSH is a secure way to connect to another computer. If you're on a mac or linux you will ssh using terminal, if you're on windows then you'll have to download (https://putty.org/). Follow online instructions for load the Raspberian operating system onto the sd card for the Raspberry Pi (https://howtoraspberrypi.com/how-to-raspberry-pi-headless-setup/). 

Once the OS is loaded onto the sd card you'll want to create files ```wpa_supplicant.conf``` and ```ssh``` so you can access you Raspberry Pi from another computer and configure it:

1) Create a file called ```ssh```, this will turn on ssh. No text has to be in the ```ssh``` file and it needs no extension.

2) Create a file called ```wpa_supplicant.conf``` and paste the follow text:
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={ 
ssid="ENTER_YOUR_WIFI_NAME_HERE" 
psk="ENTER_YOUR_WIFI_PASSWORD_HERE" 
}
```

3) transfer ```wpa_supplicant.conf``` and ```boot``` files to the boot portion of the sim card.

4) After turning on the Raspberry pi, check your network and see what the ip address is for the Pi. At the command line of terminal or putty type:
```ssh pi@ENTER_IP_ADDRESS_FOR_PI```

### Setting up the OS and packages

Before running the scripts you'll need to install some packages to get this project and have it function, at the command line type:
~~~
$ sudo apt-get -y update && sudo apt -y upgrade
$ sudo apt-get install python2.7 python3 git lirc openssl htop build-essential python-dev python-smbus
$ cd ~
$ git clone https://github.com/adafruit/Adafruit_Python_MCP3008.git # this is the ADC package for python
$ git clone git@github.com:AustinPickens/Rpi4Fish.git # clone the Rpi4Fish repository
$ sudo pip install os glob time requests datetime numpy
$ sudo pip3 install time os pyrebase json datatime
~~~~


Thee instructions will have what specific packages you need for each component interface, but these 
``` crontab -e ```

### Configuring the scheduler
We will use crontab to schedule our executable scripts to run. At the command line type:

``` crontab -e ```

Once in the crontab scheduler paste the following under the header line ```# m h  dom mon dow   command```

```
57 6 * * * /home/pi/Rpi4Fish/light_on.py
*/10 * * * * /home/pi/Rpi4Fish/main.program.py
*/15 * * * * /home/pi/Rpi4Fish/data_2_cloud.py
0 17 * * * /home/pi/Rpi4Fish/light_off.py
```

This will run the light_on.py script at 6:57 am, then launch the main.program.py every 10 minutes followed by data_2_cloud.py every 15 minutes. This staggered scheduled prevents python from getting hung up since the Raspberry Pi Zero has a single core single thread processor. In earlier versions I wrote, there were issues with scripts not finishing before the next script lanuched, and this time spacing ensures there is adequate time to log all sensor data before trying to push it to the cloud. At 5:00pm the light_off.py script will launch to shut the system down.

## Files to modify
The file master_data.json should be the only file needed to modify. In this file you will add the weather API information, your Firebase credentials, and state which components are active and ciritcal information for the program to run each component.

### Weather
Enter the city and country where it says CITY,COUNTRY. Enter API key where it says ENTER_API_KEY_HERE. The weather API information is key for the Weather simulation section to function, along with the GUI

### Firebase
Enter Google Firebase credentials here. There should be sufficient documentation available on the web to find this information on the site. I'll also put something up in a video eventually.

### Weather_simulation
active: if you will be using the IR system then active is ```true```, otherwise set it to ```false```. If set to false you can ignore the rest of the Weather_simulation fields.
LIRC_File: enter the name of your config file that contains the IR signals.
Power to default: Enter the keys you would like executed from LIRC that you had programmed. These programmed keys will also be in your LIRC file.
default: If you are missing weather condition keys, this is your default IR signal to emit. For instance the condition mist, I don't have enough weather conidtion programmed to simulate, so the light defaults to a greenish purple color settings if it doen't have a matching condition

### Tank_Info
If you are not using a water level sensor you can ignore this section. The program should know based on information you enter in the ADC_presets section that you don't have a water level sensor.

regression_inputs: The values for x correspond to the amount of water that was covering the sensor when y value was produced from the sensor. The script calibrate_water_sensor.py has more information on how these numbers are produced along with the instructions.
rectangular_tank: these are the dimensions of your fish tank. Currently it only will do math to calculate the volume of a rectangle. For height_until_full, this should be the length in inches from the bottom of the tank to the top of the water level sensor. This helps the software determine what the volume should be full so it can figure out how much water is missing from the tank.

### ADC_presets
If you have an ADC and don't have a subcomponent, then just enter a random pin. They still produce noise or a value so it shouldn't interfere with the R GUI.

active: if ```true``` then you have an ADC, otherwise set to ```false```
light_sensor: enter the pin that the light sensor is connected to
water_level_sensor: if you have one then active: is ```true``` else set to ```false```. adc_pin: enter the ADC pin for the water sensor.
reference_signal: enter the pin that is the reference signal for the water_level_sensor.
leak_sensors: enter the pins for the leak sensors

### Temp_sensors
active: if you have temperature sensors then set as ```true``` else set as ```false```
tank_bus: the bus value produced for the tank sensor. You get this value from following the temperature sensor instructions under hardware
ambient_bus: the bus value produced for the ambient sensor. You get this value from following the temperature sensor instructions under hardware.






