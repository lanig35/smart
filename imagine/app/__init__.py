# -*- coding: utf-8 -*-

from flask import Flask

# creation de l'application
app = Flask (__name__, instance_relative_config=True)

# chargement de la configuration
# 1 - par defaut (racine config)
# 2 - pour l'instance (repertoire instance)
# 3 - selon la variable d'environnement si presente
# chaque niveau ecrase le precedent si meme variable
app.config.from_object ('config.default')
app.config.from_pyfile ('config.py')
#app.config.from_envvar('APP_CONFIG_FILE')

# creation du blueprint principal
from .main import bp_main
app.register_blueprint (bp_main)

# creation du blueprint API
from .shield import bp_shield
app.register_blueprint (bp_shield, url_prefix='/shield')
