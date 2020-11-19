#!/usr/bin/env python3
# coding: utf-8

import sys, time, os, datetime, cmd, string
from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException
import linecache

# on effece l'ecran
os.system("clear")

### initialisation des paramétres date du jour et ip du serveur de sauvegarde
now = datetime.datetime.now()
scp_server = '192.168.122.36'

# Initialisation format date
hour=time.strftime('%H')
minute=time.strftime('%M')
day=time.strftime('%d')
month=time.strftime('%m')
year=time.strftime('%Y')
today=day+"-"+month+"-"+year+"-"+hour+minute

# initialisation de l'affichage du menu de sauvegarde
affichage_menu ="""
\033[34m#############################
#                           #
#\033[0m     MENU DE SAUVEGARDE\033[34m    #
#                           #
#############################\033[0m 
Choissisez une option 
\t\033[31m 1\033[0m - Switch
\t\033[31m 2\033[0m - Routeur
\t\033[31m 3\033[0m - Envoi dans le Cloud
\t\033[31m 4\033[0m - Quitter
"""
# initialisation de l'affichage du menu cloud
affiche_cloud = """
\033[34m#############################
#                           #
#\033[0m       ENVOI CLOUD S3\033[34m      # 
#                           #
#############################\033[0m 
Choissisez une option 
\t\033[31m1\033[0m  - Switch
\t\033[31m2\033[0m  - Routeur
\t\033[31m3\033[0m  - Retour
"""

# fonctions pour choisr le type de matériel à sauvegarder
def lecture_devices(device_type):
	device_type_init = device_type 							# recupération du type de matériel switch ou routeur
	chemin_listes = (f'Devices/{device_type_init}_cisco')	# chemin du fichier de parametres
	device_lecture = open(chemin_listes)					# lecture du fichier
	compteur = 0											# initialisation du compteur
	
	print(f"\nVoici la liste des {device_type_init}s")
	
	for device in device_lecture.readlines():
		infos = device.split('_')
		hostname = infos[0] 		#récupération de l'adress IP
		adress_ip = infos[1]		#récupération du login SSH
		compteur += 1				# on incrément le compteur à chaue itération
		
		### affichage de infos pour chaque matériel
		print (f'{compteur} : Nom : {hostname} - IP: {adress_ip}')
	
	choix_type_sauvegarde = int(input(f"\nEntrez votre choix de [\033[31m1-{compteur}\033[0m] ou [\033[31m0\033[0m] pour Tous : "))
	while choix_type_sauvegarde > compteur :
		try:
			choix_type_sauvegarde = int(input(f"\nEntrez votre choix de [\033[31m1-{compteur}\033[0m] ou [\033[31m0\033[0m] pour Tous : "))
			continue
		except ValueError:
			print("Oops! Ce n'est pas un nombre valide. Esaaye encore...")

	device_lecture.close()			# on ferme le fichier
	return choix_type_sauvegarde 	# on retourne le choix de l'utilisateur
			
# fonctions pour créer la sauvegarde par rapport au choix et type de materiel
def sauvegarde_devices(user_choice, device_type):
	device_type_init = device_type 										# recupération du type de matériel switch ou routeur						
	chemin_listes = (f'Devices/{device_type_init}_cisco')				# chemin du fichier de parametres
	device_lecture = open(chemin_listes)								# lecture du fichier
	ligne_choice = user_choice											# récupéaration du choix de l'utilsiateur 	
	scp_folder = (f'PROJET/P6/Sauvegarde/{device_type_init}')			# chemin du répertoire de sauvegarde
	
	# tests si choix est valide
	if ligne_choice != 0 :	
		device_visu = linecache.getline(chemin_listes, int(ligne_choice))	# récupération de la ligne choisit par l'utilisateur	
		### récupération des donnés du fichier dans des variables
		infos = device_visu.split('_')
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
			exit()
		except AuthenticationException:
			print ('Authentication Failure.')
			exit()
		except SSHException:
			print ('Make sure SSH is enabled in device.')
			exit()
		
		### initialisation de la connexion
		print ('Initiating configuration backup to ' + hostname + '\n')
		time.sleep(5)
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
		#time.sleep(10)	
		if "Destination filename" in output:
				output += net_connect.send_command_timing(command_string="\n", strip_prompt=False, strip_command=False)
		time.sleep(20)

		### Déconnexion
		net_connect.disconnect()
		print ('### Disconnecting to the device ' + adress_ip + ' is OK #### \n')

		### fermeture du fichier de settings
		device_lecture.close()
		input("Tapez sur ENTREE pour continuer...")

	elif ligne_choice == 0 :
		for device in device_lecture.readlines():
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
			print ('### Disconnecting to the device ' + adress_ip + ' is OK #### \n')
		net_connect.disconnect()
		input("Tapez sur ENTREE pour contunuer.....")
		
	else :
		print ("Erreur de saisie")
	
	### fermeture du fichier de settings
	device_lecture.close()

#############################################################################################
### Menu Option

option = "0"
while option != "4":
	os.system("clear")
	option = input(affichage_menu)

	if option == "1" :
		device_type = 'switch'
		user_choice = lecture_devices(device_type)
		sauvegarde_devices(user_choice,device_type)

	elif option == "2":
		device_type = 'routeur'
		user_choice = lecture_devices(device_type)
		sauvegarde_devices(user_choice,device_type)

	elif option == "3":
		
		option_cloud = "0"
		
		while option_cloud != "3" :
			os.system("clear")
			option_cloud = input(affiche_cloud)
			if option_cloud == "1" :
				device_type = 'switch'
				print(device_type)
				input("Tapez sur ENTREE pour contunuer.....")
			elif option_cloud == "2" :
				device_type = 'routeur'
				print(device_type)
				input("Tapez sur ENTREE pour contunuer.....")
			
	