# -*- coding: utf-8 -*-

from flask import Blueprint

bp_api = Blueprint ('api', __name__)

from . import task, author, errors
