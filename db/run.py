#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

from app import app

# mise en place journalisation
handler = RotatingFileHandler (app.config['LOG_FILE'],
                               maxBytes=app.config['LOG_BYTES'],
                               backupCount=app.config['LOG_COUNT'])
formatter = logging.Formatter ('%(asctime)s-%(levelname)s [%(module)s-%(funcName)s]: %(message)s')

handler.setFormatter (formatter)
handler.setLevel (app.config['LOG_LEVEL'])

# attachement du module de log 
app.logger.addHandler (handler)

if __name__ == "__main__":
	app.run (host=app.config['HOST'], port=app.config['PORT'])