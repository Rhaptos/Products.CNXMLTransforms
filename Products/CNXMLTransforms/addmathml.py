#!/usr/bin/env python2.3
#
# addsectiontags - parse OpenOffice XML and add section tags based on
# headings
#
# Author: Adan Galvan, Brent Hendricks
# (C) 2005 Rice University
#
# This software is subject to the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).  See LICENSE.txt for details.

import sys
from xml.sax import make_parser
from xml.sax import ContentHandler
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
from xml.sax.handler import EntityResolver
from StringIO import StringIO
import random


class docHandler(ContentHandler):

    def __init__(self):
        #  on init, create links dictionary
        self.objOOoZipFile = u''
        self.document = u''
        self.header_stack = []
        self.tableLevel = 0
        self.listLevel = 0
        self.deletion = 0
        self.handlers = {
            'draw:object':self.handleDrawObject
        }

    def handleDrawObject(self, name, end_tag, attrs={}):
        if end_tag:
            # can't get there from here ...
            # self.outputEndElement(name)
            deleteme = 0
        else:
            self.outputStartElement(name, attrs)

            strMathMLObjectName = attrs["xlink:href"]
            if strMathMLObjectName[0] == '#':
                strMathMLObjectName = strMathMLObjectName[1:len(strMathMLObjectName)]

            # HACK - need to find the object location from the manifest ...
            strMathMLObjectLocation = strMathMLObjectName + '/content.xml'

            if strMathMLObjectName:
                self.document = self.document + "<!-- embedded MathML for object: \'" + strMathMLObjectName + "\'. -->\n"
                #self.document = self.document + "<!-- embedded MathML here from location: \'" + strMathMLObjectLocation + "\'. -->\n"
                try:
                    strOOoMathML = self.objOOoZipFile.read(strMathMLObjectLocation)
                    if strOOoMathML:
                        iXmlStart = strOOoMathML.find('<math:math ')
                        if iXmlStart > 0:
                            strOOoMathMLWithoutHeader = strOOoMathML[iXmlStart:].decode('utf-8')
                            try:
                                self.document = self.document + strOOoMathMLWithoutHeader
                            except:
                                self.document = self.document + "<!-- adding to self.document failed. -->"
                        else:
                            self.document = self.document + "<!-- strOOoMathML.find(\'<math:math \') returns 0. -->\n"
                    else:
                        self.document = self.document + "<!-- self.objOOoZipFile.read(" + strMathMLObjectLocation + ") returns nothing. -->\n"
                except:
                    self.document = self.document + "<!-- self.objOOoZipFile.read(" + strMathMLObjectLocation + ") is unhappy. -->\n"

            self.outputEndElement(name)

    def startElement(self, name, attrs):
        handler = self.handlers.get(name, None)
        if handler:
            handler(name, end_tag=False, attrs=attrs)
        else:
            self.outputStartElement(name, attrs)

    def outputStartElement(self, name, attrs):
        self.document = self.document + '<%s' % name
        if attrs:
            for attr, value in attrs.items():
                self.document = self.document + " " + attr + '=%s' % quoteattr(value)
        self.document = self.document + '>'

    def characters(self, ch):
        self.document = self.document + escape(ch)

    def endElement(self, name):
        handler = self.handlers.get(name, None)
        if handler:
            handler(name, end_tag=True)
        else:
            self.outputEndElement(name)

    def outputEndElement(self, name):
        self.document += '</%s>' % name


class EntityResolver:

    def resolveEntity(self,publicId,systemId):
        return "file:///dev/null"


def addMathML(fileXml, objOOoZipFile):

    # Create an instance of the handler classes
    dh = docHandler()
    dh.objOOoZipFile = objOOoZipFile

    # Create an XML parser
    parser = make_parser()

    # Tell the parser to use your handler instance
    parser.setContentHandler(dh)
    er = EntityResolver()
    parser.setEntityResolver(er)

    # Parse the file; your handler's methods will get called
    parser.parse(fileXml)

    return dh.document.encode('UTF-8')


if __name__ == "__main__":
    file = sys.argv[1]
    f = open(file)
    print addMathML(f)
