#!/usr/bin/env python3
# coding: utf-8

import sys, time, os, datetime, cmd
from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException

###set date and time
now = datetime.datetime.now()
scp_server = '192.168.122.36'

# specify the date and time for use in the filename created on the tftp server
hour=time.strftime('%H')
minute=time.strftime('%M')
day=time.strftime('%d')
month=time.strftime('%m')
year=time.strftime('%Y')
today=day+"-"+month+"-"+year+"-"+hour+minute

###start FOR ...in 
routeur = open('Devices/switch_cisco')
scp_folder = 'PROJET/P6/Sauvegarde/switch'

for device in routeur.readlines():
	infos = device.split('_')
	hostname = infos[0]
	#récupération de l'adress IP
	adress_ip = infos[1]
	#récupération du login SSH
	user_ssh = infos[2]
	#récupération du mot de passe SSH
	mdp_ssh = infos[3]
	#récupération du mot de passe secret
	mdp_secret = infos[4]
	#recuperaton login linux pour scp
	user_linux =infos[5]
	#recuperation mot de passe user linux scp
	mdp_linux = infos[6]
	
	devices = {
		'device_type': 'cisco_ios',
		'ip': adress_ip,
		'username': user_ssh,
		'password': mdp_ssh,
		'port' : 22,          # optional, defaults to 22
		'secret': mdp_secret,     # optional, defaults to ''
	}

	print ('\n#### Connecting to the device ' + adress_ip + ' #### \n')
	try:
		net_connect = ConnectHandler(**devices)
	except NetMikoTimeoutException:
		print ('Device {} is not reachable.'.format(hostname))
		continue
	except AuthenticationException:
		print ('Authentication Failure.')
		continue
	except SSHException:
		print ('Make sure SSH is enabled in device.')
		continue

	print ('Initiating configuration backup to ' + hostname + '\n')
	net_connect = ConnectHandler(**devices)
	net_connect.enable()

	filename = hostname +'_' + str(adress_ip)+'-' + today
	save_config = 'copy startup-config scp://admin01:tssr@'+scp_server+'/'+scp_folder+'/'+filename
	print (hostname + "\033[31m saving in progress...\033[0m" + '\n')

	output = net_connect.send_command_timing(
		command_string=save_config,
		strip_prompt=False,
		strip_command=False
	)
	
	if "Address or name of remote host" in output:
			output += net_connect.send_command_timing(
			command_string="\n",
			strip_prompt=False,
			strip_command=False
			)
		
	if "Destination username" in output:
			output += net_connect.send_command_timing(
			command_string="\n",
			strip_prompt=False,
			strip_command=False
		)
	time.sleep(10)		
	if "Destination filename" in output:
			output += net_connect.send_command_timing(
			command_string="\n",
			strip_prompt=False,
			strip_command=False
		)
	time.sleep(30)	
	
	net_connect.disconnect()
	print ('### Disconnecting to the device ' + adress_ip + ' is OK #### \n')
				
print('Fin du script')

	