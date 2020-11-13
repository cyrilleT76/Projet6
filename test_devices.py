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

print ("##############################")
print ("#                            #")
print ("#      MENU SAUVEGARDE       #")
print ("#                            #")
print ("##############################")

sortie = ""
while sortie != 0:
	print ("\nChoissisez un appareil\n")
	print("1 - Switch")
	print("2 - Routeur")
	print("0 - Quitter")

	choix_device = int(input("Entrez votre choix : "))

	if choix_device == 1 :
		print ("switch")
	elif choix_device == 2 :
		print("\nVoici la liste de des routeurs")
		routeur = open('Devices/routeur_cisco')
		for device in routeur.readlines():
			infos = device.split('_')
			hostname = infos[0]
			adress_ip = infos[1]
			print("Nom: {} - IP: {}".format(hostname,adress_ip))
		print("\n")
	elif choix_device == 0:
		sortie = 0
	else :
		print("Erreur")
		sortie = 0

