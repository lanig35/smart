# -*- coding: utf-8 -*-

from flask import Blueprint

bp_shield = Blueprint ('shield', __name__)

from . import shield
