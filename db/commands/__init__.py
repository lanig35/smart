# -*- coding: utf-8 -*-
from flask_script import Manager

bases = Manager (usage=u'Gestion des bases', description=u'vvvv')
taches = Manager (usage=u'Gestion des tâches', description=u'xxx')
auteurs = Manager (usage=u'Gestion des auteurs', description=u'ccc')
livres = Manager (usage=u'Gestion des livres', description=u'xxxx')
comptes = Manager (usage=u'Gestion des utilisateurs', description=u'yyyy')
tickets = Manager (usage=u'Gestion des tickets', description=u'xxxx')

import tasktools, tickettools, usertools, booktools, dbtools, authortools
