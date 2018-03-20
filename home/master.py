#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys, os, platform, argparse
from datetime import datetime

from util import util

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description=u'Interface Imagine - broker MQTT')
group = parser.add_argument_group ('MQTT', 'Options de connexion Mosquitto')
group.add_argument ('--broker', '-b', default='127.0.0.1', help=u'adresse serveur - localhost par défaut')
group.add_argument ('--port', '-p', default=1883, type=int, help=u'port écoute - 1883 par défaut')
group.add_argument ('--id', '-i', default='smart-', help=u'préfixe id client - smart- par défaut')
group.add_argument ('--login', '-l', default='imagine', help=u'login utilisateur')
group = parser.add_argument_group ('Arduino', 'Options de connexion carte Arduino')
group.add_argument ('--serie', '-s', default='COM4', help=u'port série - COM4 par défaut')
group.add_argument ('--vitesse', '-v', default=9600, type=int, help=u'vitesse voie série - 9600 bauds par défaut')
group = parser.add_argument_group ('Debug', 'Options de debug')
group.add_argument ('--trace', '-t', action='store_true', help=u'active les traces MQTT')
group.add_argument ('--quiet', '-q', action='store_true', help=u'désactive les traces console')

args = parser.parse_args ()

# Gestion des logs
logger = util.init_log (args.login, args.quiet)

# récupération mot de passe pour connexion MQTT broker
try:
	mqtt_passwd = os.environ['MQTT_PASSWD']
except KeyError as e:
	logger.error (u'variable d\'environnement MQTT_PASSWD absente')
	exit (1)
	
# import des librairies 
try:
	import serial
	import paho.mqtt.client as mqtt
except ImportError as e:
	logger.critical (e)
	exit (1)

# définition call-backs MQTT Mosquito ('userdata' correspond au logger)
def on_connect (client, userdata, flags, rc):
	if rc != 0:
		if rc == 1:
			userdata.error (u'connexion MQTT: protocole incorrect')
		elif rc == 2:
			userdata.error (u'connexion MQTT: identifiant client invalide')
		elif rc == 3:
			userdata.critical (u'connexion MQTT: serveur non disponible')
		elif rc == 4:
			userdata.error (u'connexion MQTT: mauvais login ou mot de passe')
		elif rc == 5:
			userdata.error (u'connexion MQTT: non autorisé')
		else:
			userdata.critical (u'connexion MQTT: erreur {code}'.format(code=str(rc)))
	userdata.info (u'connexion MQTT réussie')

def on_publish (client, userdata, mid):
    userdata.info (u'MQTT: msg {0} publié'.format(str(mid)))

def on_disconnect (client, userdata, rc):
    userdata.info (u'MQTT - déconnexion: {code}'.format (code=str(rc)))

def on_log (client, userdata, level, buf):
    userdata.info ('MQTT log: {l}-{b}'.format (l=level, b=buf))

# vérification OS
platform_name = platform.system ()
if (platform_name != 'Windows') and (platform_name != 'Linux'):
	logger.critical (u'système non supporté: {0}'.format (platform_name))
	exit (1)

logger.info (u'Démarrage - MQTT: {0}-{1}-{2} Arduino: {3}-{4}'.format (
            args.broker, args.port, args.login, args.serie, args.vitesse))

# création objet Serial
ser = serial.Serial ()
ser.port = args.serie
ser.baudrate = args.vitesse
ser.timeout = 10 

# ouverture port série pour communication Arduino
try:
    ser.open () 
except serial.SerialException as e:
    logger.critical (e)	
    exit (1)

# création du client MQTT, mise en place du 'will' et infos de connexion
client = mqtt.Client (client_id=args.id+args.login, clean_session=True, userdata=logger)
client.will_set (topic='monitor/imagine', payload='hs', qos=0, retain=True)
client.username_pw_set (username=args.login, password=mqtt_passwd)

# mise en place des call-backs
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect
if args.trace is True:
	client.on_log = on_log

# tentative connection au broker MQTT
try:
    client.connect (host=args.broker, port=args.port, keepalive=60)
except IOError as e:
	logger.critical (e)
	exit (1)

# démarrage boucle évènements MQTT
client.loop_start ()

(rc, mid) = client.publish (topic='monitor/imagine', payload='in', qos=0, retain=True)

if rc != mqtt.MQTT_ERR_SUCCESS:
    logger.critical (u'erreur publication MQTT: vérifier données connexion')
    sys.exit (1)

# boucle principale de traitement des messages sur ligne série Arduino
try:
    ser.reset_input_buffer ()
    while True:
        msg = ser.readline ()
        if not msg:
            logger.warning (u'sortie sur délai d\'attente voie série')
        else:
            data = msg.split (';')
            print (data)
            ts = datetime.fromtimestamp(float(data[0])).strftime('%Y-%m-%d %H:%M:%S')
            print (ts)

            temp = data[2].split (':')
            logger.info (u'température: {t}'.format (t=float(temp[1])))
            (rc, mid) = client.publish (topic=data[1]+'/temp', payload=float(temp[1]), qos=0, retain=False)
            if rc != mqtt.MQTT_ERR_SUCCESS:
                logger.critical (u'erreur publication MQTT: vérifier données connexion')
                sys.exit (1)
            print (rc, mid)
            lum = data[3].split(':')
            logger.info (u'température: {t}'.format (t=float(lum[1])))
            (rc, mid) = client.publish (topic=data[1]+'/lum', payload=int(lum[1]), qos=0, retain=False)
            if rc != mqtt.MQTT_ERR_SUCCESS:
                logger.critical (u'erreur publication MQTT: vérifier données connexion')
                sys.exit (1)
            print (rc, mid)
except KeyboardInterrupt as e:
    ser.close ()
    client.disconnect ()
    logger.info (u'arrêt du programme')

