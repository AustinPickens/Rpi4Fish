# Rpi4Fish
Automated Fish Tank System Using Raspberry Pi, Python, and R Shinny for Graphic User Interface.

## Background
Rpi4Fish is an open source project developed to control and monitor your fish tank, however, the core functionality can easily be modified for many other applications. The inspiration for this project started when I purchased a fish tank light that can simulate weather conditions using an infrared remote, I thought to myself "it would be so cool if a computer could check the weather report, then change the light in by emitting the same infrared signal as the remote". Rpi4Fish utilizes the microcontroller raspberry pi (i.e., Raspberry Pi Zero W) to execute scripts written in the programming language Python, which log data from sensors configured to the Raspberry Pi. The data is then pushed to a cloud NoSQL database. Finally, using R shiny, the data is pulled into a graphic user interface (GUI) that displays all the data at https://Rpi4Fish.com. You can download R and run the website locally using data generated from my fish tank, so you do not need any of the hardware to get something from the project. You can host the application through https://www.shinyapps.io, and you get 25 hours of free service a month -OR- you can host your own cloud server and website like I did for https://Rpi4Fish.com .

I rewrote all the source code in such a way where someone with no experience could walk through and understand what is happening. 

## Hardware Instructions

## Setting up the scripts
Before running the scripts we wil

## Files to modify
The file master_data.json should be the only file needed to modify.

### Weather
enter the city and country where it says CITY,COUNTRY. Enter API key where it says ENTER_API_KEY_HERE. The weather API information is key for the Weather simulation section to function, along with the GUI

### Firebase
Enter Google Firebase credentials here. There should be sufficient documentation available on the web to find this information on the site.

### Weather Simulation
active: if you will be using the IR system then active is true, otherwise set it to false. If set to false you can ignorethe rest of the Weather_simulation fields.
LIRC_File: enter the name of your config file that contains the IR signals
Power to default: Enter the you would like executed from LIRC that you had programmed. These programmed keys will also be in your LIRC file.
default: If you are missing weather condition keys, this is your default IR signal to emit. For instance the condition mist, I don't have enough weather conidtion programmed to simulate, so the light defaults to a greenish purple color settings if it doen't have a matching condition
