# Sauvegarde automatiser de Routeur/Switch Cisco et envoi dans le Cloud S3
> Le but de ce script est de sauvegarder la configuration de routeur ou de switch Cisco el local, en créant un fichier pour chaque matériels, puis de les envoyer dans le cloud AWS3.

## Table des matieres
* [Prérequis](#Prérequis)
* [Utilisation](#Utilisation)
* [Fonctionnement](#Fonctionnement)
* [Contact](#Contact)

## Prérequis
Testé sous linux debian 10
Materiels cisco ou virtuel avec GNS3
Version python 3.7
pip install requirement.txt
Bucket sur AWS 3

## Configuration/parametre
Utilisation du fichier config.yaml pour saisir vos parametres de sauvegarde

## Fonctionnement
* Menu SAUVEGARDE:
 1- switch ->
 2- routeur
 3- envoi cloud
 4- quitter
* Menu CLOUD:
 1- switch
 2- routeur
 3- quitter

## Contact
Created by [@flynerdpl](https://www.flynerd.pl/) - feel free to contact me!
