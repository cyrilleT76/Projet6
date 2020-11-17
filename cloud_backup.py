#!/usr/bin/env python3
# coding: utf-8

import boto3
import os

# Let's use Amazon S3
s3 = boto3.client('s3')

# # Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)

chemin_sauvegarde = './Sauvegarde/routeur'

for fichiers in os.listdir(chemin_sauvegarde):
	print(fichiers)
	
	upload_file_bucket = 'save-config-p6'
	upload_file_key = 'routeur/' + str(fichiers)
	fichiers = chemin_sauvegarde + '/' + fichiers
	# 	tests_chemin = s3.upload_file(file, upload_file_bucket, upload_file_key)
	# 	print(tests_chemin)
	s3.upload_file(fichiers, upload_file_bucket, upload_file_key)
	