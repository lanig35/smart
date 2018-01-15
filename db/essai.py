#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')
import io

print sys.getdefaultencoding()

print ('états')
print ('états')

print sys.argv

print sys.argv[1]
d = sys.argv[1].decode ('cp1252')
print d
print type(d)

#sys.argv[1] = unicode (sys.argv[1], 'cp1252') 
print sys.argv
