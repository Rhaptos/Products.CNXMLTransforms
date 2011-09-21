#! /usr/bin/env python
import sys
import os
import random
from Globals import package_home
from xml.sax import make_parser
from xml.sax import ContentHandler, InputSource
from xml.sax.saxutils import escape
from xml.sax.handler import EntityResolver, feature_external_ges
from StringIO import StringIO

HTML2CNXML_XSL = os.path.join(package_home(globals()), 'www', 'html2cnxml.xsl') 
MATHML_ENTITIES = 'file:///usr/share/xml/mathml/schema/dtd/2.0/moz-mathml.ent'

class docHandler(ContentHandler):

    def __init__(self):
        #  on init, create links dictionary
        self.document = u''
        self.header_stack = ['h0']
        self.tableLevel = 0
        self.handlers = {
            'table':self.handleTable,
            'h1':self.handleHeader,
            'h2':self.handleHeader,
            'h3':self.handleHeader,
            'h4':self.handleHeader,
            'h5':self.handleHeader,
            'h6':self.handleHeader,
            'body':self.handleBody
            }


    def handleTable(self, name, end_tag, attrs={}):
        if end_tag:
            self.tableLevel -= 1
            self.outputEndElement(name)
        else:
            self.tableLevel += 1
            self.outputStartElement(name, attrs)
        
    def handleHeader(self, name, end_tag, attrs={}):
        if self.tableLevel:
            return

        if not end_tag:
            self.endSections(name)
            
            id = attrs.get('id',self.generateId())
            self.document = self.document + "<section id='%s'>\n" %id
            self.document = self.document + "<name>"
        else:
            self.document = self.document + "</name>"


    def handleBody(self, name, end_tag, attrs={}):
        #head-> name
        if not end_tag:
            self.document = self.document + '<body'
            if attrs:
                for attr, value in attrs.items():
                    self.document = self.document + " " + attr + '="%s"' % value
            self.document = self.document + '>'
        else:
	    self.endSections()
            self.document = self.document + '</body>'

    
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
                self.document = self.document + " " + attr + '="%s"' % value
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

    def storeSectionState(self, name):
        """
        Takes a header tagname (e.g. 'h1') and adjusts the 
        stack that remembers the headers seen.
        """
        while True:
            if name < self.header_stack[-1]:
                del(self.header_stack[-1])
            elif name == self.header_stack[-1]:
                return
            elif name > self.header_stack[-1]:
                self.header_stack.append(name)
                return
        
    def endSections(self, name='h1'):
        """Closes all sections of level >= sectnum. Defaults to closing all open sections"""
	
        oldSectnum = len(self.header_stack)
        self.storeSectionState(name)
        newSectnum = len(self.header_stack)
        self.document = self.document + "</section>\n" * (oldSectnum - (newSectnum-1))
	

    def generateId(self):
        return 'id-' + str(random.random())[2:]

    def skippedEntity(self, name):
        print "Skipping " + name
    

class EntityResolver:

    def resolveEntity(self,publicId,systemId):
        return MATHML_ENTITIES
    
def addSectionTags(content):

    from cStringIO import StringIO
    src = InputSource()
    src.setByteStream(StringIO(content))

    # Create an XML parser
    parser = make_parser() #("xml.sax.drivers2.drv_xmlproc")
    
    dh = docHandler()
    parser.setContentHandler(dh)

    er = EntityResolver()
    parser.setEntityResolver(er)

    # Allow external entities
    parser.setFeature(feature_external_ges, True)
    
    # Parse the file; your handler's methods will get called
    parser.parse(src)

    return dh.document.encode('UTF-8')

def xsl_transform(content):
    import libxml2
    import libxslt

    #Parse stylesheet
    styleParser = libxml2.createFileParserCtxt(HTML2CNXML_XSL)
    #styleParser.replaceEntities(1)
    styleParser.parseDocument()
    styledoc = styleParser.doc()
    style = libxslt.parseStylesheetDoc(styledoc)

    #Parse document
    docParser = libxml2.createMemoryParserCtxt(content, len(content))
    #docParser.replaceEntities(1)
    docParser.parseDocument()
    doc = docParser.doc()

    resultDoc = style.applyStylesheet(doc, None)
    if resultDoc:
        result = style.saveResultToString(resultDoc)
        resultDoc.freeDoc()
    else:
        raise ValueError, "Unable to perform transform " + stylesheet
    style.freeStylesheet()
    doc.freeDoc()

    return result

def html_to_cnxml(content):
    content = addSectionTags(content)
    content = xsl_transform(content)
    content = content.replace('xmlns="http://www.w3.org/1999/xhtml"','')
    return content

if __name__ == "__main__":
    f = open(sys.argv[1])
    content = f.read()
    print html_to_cnxml(content)
