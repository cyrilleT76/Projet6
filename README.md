# Sauvegarde automatisée de Routeur/Switch Cisco et envoi dans le Cloud S3
>Le but de ce script est de sauvegarder la configuration de routeur ou de switch Cisco en local, en créant un fichier pour chaque matériels dans un répertoire donné, puis de les envoyer et les sauvegarder dans le cloud AWS3 avec une date d'expiration, afin de pas surcharger ce dernier.

## Table des matieres:
* [Prérequis](#Prérequis)
* [Utilisation](#Utilisation)
* [Fonctionnement](#Fonctionnement)
* [Contact](#Contact)

## Prérequis :
Linux, testé sous debian 10  
Materiels cisco réels ou virtuels avec GNS3  
Version python 3, testé sous 3.7   
pip install *[requirements.txt](https://github.com/cyrilleT76/Projet6/blob/master/requirements.txt)* pour les bibliothéques supplémentaires  
Bucket actif sur AWS3     
Installation de [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install) pour la gestion du Bucket   
Compte et mot de passe SSH sur matériels cisco, et mot de passe ENABLE d'activé  
Compte et mot de passe Linux sur server SCP

## Configuration/Paramètres :
Utilisation du fichier *[config.yaml](https://github.com/cyrilleT76/Projet6/blob/master/config.yaml)* pour saisir vos parametres de sauvegarde  

    scp_server: 192.168.122.36  
    delai_expiration: 10 
    nom_bucket: save-config-p6 


Utilisation du dossier *Devices* avec les 2 fichiers *routeur_cisco* et *switch_cisco* pour les informations (adresse ip, mot de passe etc...) des routeurs et des switchs    
>EX: ***nom_adresseIP_userSSH_mdpSSH_mdpEnableSecret_userLinux_mdpUserLinux_***   

Création d'un répertoire *Sauvegarde* avec deux sous répertoires *switch* et *routeur* pour stocker les fichier de configuration de chaque matériels   

## Fonctionnement :
Sous linux, exécuter le fichier *[Backup_devices.py](https://github.com/cyrilleT76/Projet6/blob/master/Backup_device.py)*   

    $./Backup_devices.py   

pour afficher le menu suivant   

* **Menu SAUVEGARDE:**     
    1.Switch -> en tapant 1 cela affiche la listes des switchs, on peux en sélectionner un seul via son N° ou tous en tapant 0    

        le fichier genere est formaté ainsi : nom + adresse + date  

    2.Routeur -> en tapant 2 cela affiche la listes des routeurs, on peux en sélectionner un seul via son N° ou tous en tapant 0    

        le fichier genere est formaté ainsi : nom + adresse + date

    3.Envoi cloud -> ouvre le menu cloud ci dessous  

    4.Quitter -> pour quiter le scritp  

* **Menu CLOUD:**     
    1.Switch -> effectue une sauvegarde dans le cloud S3 de tous les fichiers inferieurs à la date d'expiration 
    
        EX: ici 10 jours dans fichier config.yaml  

    2.Routeur - > effectue une sauvegarde dans le cloud S3 de tous les fichiers inferieurs à la date d'expiration  
    
        EX: ici 10 jours dans fichier config.yaml     

    3.Quitter  

## Contact :
Réalisé par [toutain.cyrille@gmail.com] - feel free to contact me!
