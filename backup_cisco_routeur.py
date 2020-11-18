#!/usr/bin/env python3
# coding: utf-8

import sys, time, os, datetime, cmd
from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException

### initialisation de la date et du serveur de sauvegarde
now = datetime.datetime.now()
scp_server = '192.168.122.36'

### creation d'un format de date
hour=time.strftime('%H')
minute=time.strftime('%M')
day=time.strftime('%d')
month=time.strftime('%m')
year=time.strftime('%Y')
today=day+"-"+month+"-"+year+"-"+hour+minute

### chemin de la configuration
routeur = open('Devices/routeur_cisco')
scp_folder = 'PROJET/P6/Sauvegarde/routeur'

for device in routeur.readlines():
	infos = device.split('_')
	hostname = infos[0] 		#récupération de l'adress IP
	adress_ip = infos[1]		#récupération du login SSH
	user_ssh = infos[2]			#récupération du mot de passe SSH
	mdp_ssh = infos[3]			#récupération du mot de passe secret
	mdp_secret = infos[4]		#recuperaton login linux pour scp
	user_linux =infos[5]		#recuperation mot de passe user linux scp
	mdp_linux = infos[6]
	
	devices = {
		'device_type': 'cisco_ios',
		'ip': adress_ip,
		'username': user_ssh,
		'password': mdp_ssh,
		'port' : 22,          
		'secret': mdp_secret,    
	}

	print ('\n#### Connecting to the device ' + adress_ip + ' #### \n')
### test de la connexion SSH
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
	
### initialisation de la connexion
	print ('Initiating configuration backup to ' + hostname + '\n')
	net_connect = ConnectHandler(**devices)
	net_connect.enable()

### creation de la commande pour la sauvagarde
	filename = hostname +'_' + str(adress_ip)+'-' + today
	save_config = 'copy startup-config scp://'+user_linux+':'+mdp_linux+'@'+scp_server+'/'+scp_folder+'/'+filename
	print (hostname + "\033[31m saving in progress...\033[0m" + '\n')
	
#### envoie de la commande et validation des messages dans la console CLI cisco
	output = net_connect.send_command_timing(command_string=save_config,strip_prompt=False,strip_command=False)
	if "Address or name of remote host" in output:
			output += net_connect.send_command_timing(command_string="\n", strip_prompt=False, strip_command=False)
	if "Destination username" in output:
			output += net_connect.send_command_timing(command_string="\n", strip_prompt=False, strip_command=False)
	if "Destination filename" in output:
			output += net_connect.send_command_timing(command_string="\n", strip_prompt=False, strip_command=False)

### Déconnexion
	net_connect.disconnect()
	print ('### Disconnecting to the device ' + adress_ip + ' is OK #### \n')
				
print('Fin du script')

	