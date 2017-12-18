# -*- coding: utf-8 -*-
from flask import current_app

from . import bp_shield

from .. import Arduino
import time

# rajouter try/catch et port en argument
board = Arduino.Arduino (baud=9600, port='COM4')
while board.version() != 'Alain':
    print 'attente'
    time.sleep (1)

@bp_shield.route ('/')
def index():
    current_app.logger.info ('request')
    return (u'Shield!')

@bp_shield.route ('/version', methods=['GET'])
def version():
    return board.version()

@bp_shield.route ('/sensors/temp', methods=['GET'])
def get_temp ():
    sensor = board.analogRead (2)
    print sensor
    voltage = (sensor / 1024.0) * 5.0
    temp = (voltage - 0.5) * 100
    return str(temp)

@bp_shield.route ('/leds', methods=['DELETE'])
def clear_led ():
    board.shiftOut (3, 2, "MSBFIRST", 0b00000001)
    return 'ok'
