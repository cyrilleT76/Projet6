#!/usr/bin/env python3
# coding: utf-8

import sys, time, os, cmd, string
import linecache
import boto3
import yaml

from datetime import datetime, timedelta
from netmiko import ConnectHandler
from getpass import getpass
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException


with open("config.yaml", "r") as configfile:
	cfg = yaml.load(configfile)

# on efface l'ecran
os.system("clear")

### initialisation des paramétres 
scp_server = cfg["scp_server"]
delai_expiration = cfg["delai_expiration"]

# date du jour
tday = time.time()
duration = 86400 * int(delai_expiration) # nombre de  jours

# contrôle pour la suppression
expire_limit = tday - duration

# initialise s3 client
s3_client = boto3.client('s3')
my_bucket = cfg["nom_bucket"]
file_size = [] # juste pour suivre les économies totales en termes de taille de stockage

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

##########################################################################################################################
### SAUVEGARDE MATERIELS

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
			print("Oops! Ce n'est pas un nombre valide. Essaye encore...")

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
			if "Destination filename" in output:
					output += net_connect.send_command_timing(command_string="\n", strip_prompt=False, strip_command=False)
			time.sleep(20)

			### Déconnexion
			print ('### Disconnecting to the device ' + adress_ip + ' is OK #### \n')
		net_connect.disconnect()
		input("Tapez sur ENTREE pour continuer.....")
		
	else :
		print ("Erreur de saisie")
	
	### fermeture du fichier de settings
	device_lecture.close()

##########################################################################################################################
### SAUVEGARDE S3  

# Initialisation pour AWS3
s3 = boto3.client('s3')

def get_creation_date(file):
	stat = os.stat(file)
	try:
		return stat.st_birthtime
	except AttributeError:
		return stat.st_mtime

def sauvegarde_cloud_S3 (device_type_cloud):
	# Initialisation pour AWS3
	s3 = boto3.client('s3')
	chemin_sauvegarde = f'./Sauvegarde/{device_type_cloud}'

	# récupération de la date jour
	today = datetime.today()

	# date du jour moins 10 jours
	expected_date = today - timedelta(days=10)

	for fichiers in os.listdir(chemin_sauvegarde):
		
		upload_file_bucket = my_bucket
		upload_file_key = f'{device_type_cloud}/{fichiers}'
		upload_fichiers = f'{chemin_sauvegarde}/{fichiers}'
		
		# Convertir Timestamp en datetime
		creation_date = datetime.fromtimestamp(get_creation_date(upload_fichiers))
		if creation_date > expected_date:
			print(f"\033[34mFichiers Sauvegardés à J-10 : {fichiers}\033[0m " )
			print("\t\033[32mDate de création: %s \033[0m" % creation_date)
			print("\t\033[32mDate d'expiration: %s \033[0m" % (creation_date + timedelta(days=10)))
			s3.upload_file(upload_fichiers, upload_file_bucket, upload_file_key)
		#elif creation_date < expected_date:
			#s3.delete_object(Bucket=upload_file_bucket+'/'+ device_type_cloud +'/',Key=fichiers)
		else :
			print(f"\033[31mFichiers non Sauvegardés : {fichiers}\033[0m")
			print(f"\t\033[31mDate de création: {creation_date}")
			print(f"\t\033[31mA expiré le : {(creation_date + timedelta(days=10))}")

##########################################################################################################################
### SUPPRESSION SUR S3 FICHIERS > DATE JOUR -10 ex: nous sommes le 13/12, les fichiers avant le 3/12 seront supprimés

# Fonctions
def get_key_info(bucket, prefix):

	print(f"Voici le nom, la taille et la date des fichiers dans le Bucket S3: {bucket} dans le répertoire: {prefix}")

	key_names = []
	file_timestamp = []
	file_size = []
	kwargs = {"Bucket": bucket, "Prefix": prefix}
	while True:
		response = s3_client.list_objects_v2(**kwargs)
		for obj in response["Contents"]:
			# exclure les annuaires/dossiers des résultats. Supprimer cette option si les dossiers doivent également être supprimés
			if "." in obj["Key"]:
				key_names.append(obj["Key"])
				file_timestamp.append(obj["LastModified"].timestamp())
				file_size.append(obj["Size"])
		try:
			kwargs["ContinuationToken"] = response["NextContinuationToken"]
		except KeyError:
			break

	key_info = {
		"key_path": key_names,
		"timestamp": file_timestamp,
		"size": file_size
	}
	print(f'Toutes les fichiers dans le Bucket : {bucket} avec pour répertoire : {prefix} ont été trouvées !')
	return key_info


# Vérifiez si la date dépassée est antérieure à la date limite
def check_expiration(key_date=tday, limit=expire_limit):
	if key_date < limit:
		return True

# se connecter à s3 et supprimer le fichier
def delete_s3_file(file_path, bucket=my_bucket):
	print(f"Suppression de {file_path}")
	s3_client.delete_object(Bucket=bucket, Key=file_path)
	return True

# verification taille effacée
def total_size_dltd(size):
	file_size.append(size)
	del_size = round(sum(file_size)/1.049e+6, 2) # conversion byte en megabyte
	return del_size
		
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
				
				device_type_cloud = 'switch'
				sauvegarde_cloud_S3(device_type_cloud)
				
				try:
					s3_file = get_key_info(my_bucket,device_type_cloud)
					del_size  = 0
					for i, fs in enumerate(s3_file["timestamp"]):
						file_expired = check_expiration(fs)
						if file_expired: #if True is recieved
							file_deleted = delete_s3_file(s3_file["key_path"][i])
							if file_deleted: #if file is deleted
								del_size = total_size_dltd(s3_file["size"][i])

					print(f"Taille totale du/des fichier(s) supprimé(s) :{del_size} MB")
				except:
					print ("échec:", sys.exc_info()[1])
					print(f"Taille totale du/des fichier(s) supprimé(s) : {del_size} MB")

				input("Tapez sur ENTREE pour contunuer.....")

			elif option_cloud == "2" :
				device_type_cloud = 'routeur'
				
				# appelle de la fonction pour sauvegarder dans le cloud
				sauvegarde_cloud_S3(device_type_cloud)

				# suppresssion des fichiers supérieurs à 10 jours dans le cloud
				try:
					s3_file = get_key_info(my_bucket,device_type_cloud)
					del_size  = 0
					for i, fs in enumerate(s3_file["timestamp"]):
						file_expired = check_expiration(fs)
						if file_expired: #if True is recieved
							file_deleted = delete_s3_file(s3_file["key_path"][i])
							if file_deleted: #if file is deleted
								del_size = total_size_dltd(s3_file["size"][i])

					print(f"Taille totale du/des fichier(s) supprimé(s) :{del_size} MB")
				except:
					print ("échec:", sys.exc_info()[1])
					print(f"Taille totale du/des fichier(s) supprimé(s) : {del_size} MB")
				
				input("Tapez sur ENTREE pour contunuer.....")
			
	