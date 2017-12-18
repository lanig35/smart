# -*- coding: utf-8 -*-

from flask import Blueprint

bp_main = Blueprint ('main', __name__)

from . import errors, main
