#!/usr/bin/python
#python 3

"""
	Device Scanning, CNC connect

	-Retrieve command from cnc server (endpoint in config file)
		[format]: nmap instruction from cnc server: (xXx)sudo nmap(xXx)  "cmd ip/s"  (xXx)-ox fnmae(xXx)
	-Run nmap command and POST to cnc server (json) while retrieving next command
	-Repeate

	[todo]: 
			-fault tolorence to down server
			-cmds:quit,start,stop #for direct user ssh input
			-display hud instead of nmap output: uptime, last connection time, last command, scanning, [cmds list]
			-run nmap as subprocess to rejoin on scan completion
			-error specific
			-fix ports bug
"""

#
#	imports
#

# standard
import os
import requests
import sys
import json
from libnmap.parser import NmapParser
from xml.parsers import expat
from decimal import *
import time

#
#	settings
#

# general
ERROR_STRING = '-1'

# configuration settings
config_fname = "../scanner_config.cfg"			#resource
DEVICE_NAME_KEY = "DEVICE_NAME"
CNC_URL_KEY = "CNC_URL"
NMAP_XML_FNAME_KEY = "NMAP_XML_FNAME"
DEFAULT_VALUE_KEY = "DEFAULT_VALUE"
#
#	functions
#

# pull value from config file
def config_value(config_fname, key):
	setting_value = ERROR_STRING

	with open(config_fname, 'r') as f:
		default_settings = f.read()

	default_settings = default_settings.split('\n')
	for line in default_settings:
		setting = line.split('=')

		if setting[0] == key:
			setting_value = setting[1]

	return setting_value

# convert nmap xml output to json object for payload to cnc
def xmlf_to_payload(xml_fname, nmap_cmd):

	try:
		#parse data
		report = NmapParser.parse_fromfile(xml_fname) #NmapParse module is opening the XML file
	except:
		print ("error nmap xml format")
		return ERROR_STRING

	### scan information
	nmapscan_started = int(report.started)
	nmapscan_elapsed = str(report.elapsed)
	nmapscan_commandline = str(report.commandline)
	hosts_attempted = str(report.hosts_total)
	nmapscan_scan_type = str(report.scan_type)

	scan_object = {}
	scan_object['parent_name'] = config_value(config_fname, DEVICE_NAME_KEY) or ERROR_STRING
	scan_object['start_time'] = nmapscan_started
	scan_object['time_elapsed'] = nmapscan_elapsed
	scan_object['scan_type'] = nmapscan_scan_type
	scan_object['nmap_command'] = nmap_cmd
	scan_object['hosts_attempted'] = hosts_attempted
	scan_object['hosts'] = []

	### host information
	for _host in report.hosts:
		host_object = {}
		### host info
		host_object['host_ipv4']  = _host.ipv4 or config_value(config_fname, DEFAULT_VALUE_KEY)
		host_object['host_ipv6']  = _host.ipv6 or config_value(config_fname, DEFAULT_VALUE_KEY)
		host_object['mac'] = _host.mac or config_value(config_fname, DEFAULT_VALUE_KEY)
		host_object['os'] = _host.os.osmatches or config_value(config_fname, DEFAULT_VALUE_KEY)
		host_object['vendor'] = _host.vendor or config_value(config_fname, DEFAULT_VALUE_KEY)
		### scan info
		host_object['start_time'] = _host.starttime or config_value(config_fname, DEFAULT_VALUE_KEY)
		host_object['end_time'] = _host.endtime or config_value(config_fname, DEFAULT_VALUE_KEY)
		### port information
		host_object['ports'] = [{'port_number':x[0],'port_service':x[1]} for x in _host.get_open_ports()]
		scan_object['hosts'].append(host_object)

	return json.dumps(scan_object)

# run nmap command and output to xml file, return json string or defualt value
def run_nmap_cmd(nmap_cmd):
	try:
		#run scan
		os.system('sudo nmap ' + nmap_cmd + ' -oX ' + config_value(config_fname, NMAP_XML_FNAME_KEY))
		return xmlf_to_payload(config_value(config_fname, NMAP_XML_FNAME_KEY), nmap_cmd)
	except: 
		print (sys.exc_info()[0])
		print ("error: f:scan.py: failed to run nmap_command")
		return ERROR_STRING

# POST scan_json to cnc endpoint, return cnc cmd or default value
def connect_cnc(scan_json):
	try:
		response = requests.post(config_value(config_fname, CNC_URL_KEY), json=scan_json)
		if response.status_code == 200:
			return response.text
	except: 
		print ("error: f:scan.py: failed connecting to server")
	return ERROR_STRING

# main loop
def main(args=None):		#arg stuff propably not necissary
	if args is None:
		args = sys.argv[1:]

	nmap_cmd = ERROR_STRING
	scan_json = ERROR_STRING

	while True:

		# send nmap scan json and get next nmap command
		nmap_cmd = connect_cnc(scan_json)

		#display command
		print ("\nNEXT NMAP COMMAND FROM CNC: " + nmap_cmd)

		# run nmap command and get scan json
		scan_json = run_nmap_cmd(nmap_cmd)

		#allows exit cmd
		time.sleep(.5)

"""
									run program
"""

if __name__ == "__main__":
	main()
