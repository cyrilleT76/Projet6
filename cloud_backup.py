#!/usr/bin/env python3
# coding: utf-8

import boto3
import os
from datetime import datetime, timedelta

# Let's use Amazon S3
s3 = boto3.client('s3')

# # Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)

def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        # Nous sommes probablement sous Linux. Pas de moyen pour obtenir la date de création, que la dernière date de modification.
        return stat.st_mtime

chemin_sauvegarde = './Sauvegarde/routeur'

# récupération de la date jour
today = datetime.today()

# date du jour moins 4 jours
expected_date = today - timedelta(days=4)

for fichiers in os.listdir(chemin_sauvegarde):
	
	
	upload_file_bucket = 'save-config-p6'
	upload_file_key = 'routeur/' + str(fichiers)
	upload_fichiers = chemin_sauvegarde + '/' + fichiers
	
	
	# Convertir Timestamp en datetime
	creation_date = datetime.fromtimestamp(get_creation_date(upload_fichiers))
	if creation_date > expected_date:
		 print(f"\033[34mFichiers Sauvegardés à J-10 : {fichiers}\033[0m " )
		 print("\t\033[32mDate de création: %s \033[0m" % creation_date)
		 print("\t\033[32mDate expiration: %s \033[0m" % expected_date)
		 #s3.upload_file(upload_fichiers, upload_file_bucket, upload_file_key)
	else :
		print(f"\033[31mFichiers non Sauvegardés : {fichiers}\033[0m")
		