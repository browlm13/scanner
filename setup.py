#!/usr/bin/env pytho
#python 3

#
#	imports
#

# standard
import os
import io #new for ubuntu

#internal
import src.config_handler as config_handler

#
#config settings
#

#scanner
scanner_cfg_fname = "scanner_config.cfg"
scanner_name_key = "DEVICE_NAME"

#
#	install dependencies
#

os.system('sudo apt-get update')
os.system('sudo apt-get install tmux')
os.system('sudo apt-get install nmap')
os.system('sudo pip install python-libnmap')

#
#	capture device name
#

#set permisions
os.system('sudo chmod 755 ' + scanner_cfg_fname)

device_name = input('Enter your device name: ')
config_handler.set_value(scanner_cfg_fname, scanner_name_key, device_name)
