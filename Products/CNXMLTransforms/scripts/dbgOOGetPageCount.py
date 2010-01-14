#!/usr/bin/env python2.4

# Python-UNO bridge
# http://udk.openoffice.org/python/python-bridge.html
# PyUNO can be used in three different modes:
#
#   1. Inside the OpenOffice.org process within the scripting framework (OOo 2.0 and later only !!),
#   2. Inside the python executable (and outside the OOo process)
#   3. Inside the OpenOffice.org (OOo) process

import os
import sys
import uno
from unohelper import Base,systemPathToFileUrl, absolutize
from os import getcwd
from com.sun.star.beans import PropertyValue

# import pdb
# pdb.set_trace()

dirs=sys.argv[1:]

address = "localhost:2002"
host, port = address.split(':')
port = int(port)

url = "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext" % (host, port)

ctxLocal = uno.getComponentContext()
smgrLocal = ctxLocal.ServiceManager

resolver = smgrLocal.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", ctxLocal )
ctx = resolver.resolve( url )
smgr = ctx.ServiceManager

desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx )

startpwd = os.getcwd()

result_file = startpwd + '/result.txt'
print 'writing results to: ' + result_file
result=open(result_file, 'w')

for dir in dirs:
#dir = dirs[0]
#if True: 
    os.chdir(dir)
    files = os.listdir(dir)
    cwd = systemPathToFileUrl( os.getcwd() )

    print "for directory '" + dir + "' we found " + str(len(files)) + " files."

    for file in files:
        if file.endswith('.xml'):
            print 'skipping: ' + file
            continue

        try:
            inProps = (PropertyValue( "Hidden" , 0 , True, 0 ),)
            fileUrl = uno.absolutize( cwd, systemPathToFileUrl(file) )
            doc = desktop.loadComponentFromURL( fileUrl, "_blank", 0, inProps)

            cursor = doc.getCurrentController().getViewCursor()
            cursor.jumpToLastPage()
            page_count = cursor.getPage()
            print file + ',' + str(page_count)
            result.write(str(page_count) + '\n')
            result.flush()
            doc.dispose()
        except:
            pass

result.close()
