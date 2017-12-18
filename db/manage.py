#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
#os.environ['APP_CONFIG_FILE'] = '/home/ec2-user/training/config/default.py'

import time
import logging
from logging.handlers import RotatingFileHandler

from flask import current_app

from flask_script import Manager
from app import app

# creation du manager
manager = Manager (app)

@manager.command
def secret ():
    u"Géneration clé secrète"
    current_app.config['logger'].info (u'secret')
    print os.urandom(24).encode('hex')

# mise en place des commandes groupées
from commands import taches, tickets, livres, auteurs, comptes, bases
manager.add_command (u'bases', bases)
manager.add_command (u'taches', taches)
manager.add_command (u'auteurs', auteurs)
manager.add_command (u'livres', livres)
manager.add_command (u'comptes', comptes)
manager.add_command (u'tickets', tickets)

if __name__ == "__main__":
    # mise en place journalisation
    logger = logging.getLogger (u'manage')
    logger.setLevel (app.config['LOG_LEVEL'])

    handler = RotatingFileHandler (filename=app.config['CMD_LOG_FILE'], mode='a',
                                   maxBytes=app.config['LOG_BYTES'],
                                   backupCount=app.config['LOG_COUNT'],
                                   encoding='utf-8', delay=False)
    formatter = logging.Formatter (fmt='%(asctime)s;%(module)s;%(funcName)s;%(levelname)s;%(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
 
    # timestamp des logs en GMT/UTC
    formatter.converter = time.gmtime

    handler.setFormatter (formatter)
    handler.setLevel (app.config['LOG_LEVEL'])

    # attachement du module de log
    logger.addHandler (handler)

    if app.config.get('DEBUG'):
        stream_handler = logging.StreamHandler ()
        stream_handler.setFormatter (formatter)
        stream_handler.setLevel (app.config['LOG_LEVEL'])
        logger.addHandler (stream_handler)

    app.config['logger'] = logger

    # désactivation logging Flask
    app.logger.disabled = True

    # lancement du programme
    manager.run ()

