# -*- coding: utf-8 -*-
from flask import current_app

from . import bp_main

@bp_main.route ('/')
def index():
    current_app.logger.info ('request')
    return (u'Hello todo!')

