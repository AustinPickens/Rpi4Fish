#!/usr/bin/env python3.4
import time, os, pyrebase, json
from datetime import datetime

## Open credentials file
credentials_in=open(os.getcwd() +'/Rpi4Fish/master_data.json')
credentials=json.load(credentials_in)

## Establish connection
firebase = pyrebase.initialize_app(credentials['Firebase'])

## Get a reference to the auth service
auth = firebase.auth()

## Log the user in
user = auth.sign_in_with_email_and_password(credentials['Firebase']['user'], credentials['Firebase']['password'])


## Get a reference to the database service
db = firebase.database()

## Open sensor data logged from main_program.py
tmp=open('Data_from_sensors.json')
data = json.load(tmp)

## Push current conditions to database
db.child("Condition").update(data['Conditions'], user['idToken'])

## Push sensor data to database
db.child("Data").push(data['Values'], user['idToken'])
