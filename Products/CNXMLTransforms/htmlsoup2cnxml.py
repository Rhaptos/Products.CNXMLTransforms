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

XHTML_ENTITIES = os.path.join(package_home(globals()), 'www', 'catalog_xhtml', 'catalog.xml')
GDOCS2CNXML_XSL1 = os.path.join(package_home(globals()), 'www', 'gdocs_meta1.xsl') 
GDOCS2CNXML_XSL2 = os.path.join(package_home(globals()), 'www', 'gdocs_meta2.xsl') 
# Just for debugging:
# XHTML_ENTITIES = os.path.join('.', 'www', 'catalog_xhtml', 'catalog.xml')
# GDOCS2CNXML_XSL1 = os.path.join('.', 'www', 'gdocs_meta1.xsl') 
# GDOCS2CNXML_XSL2 = os.path.join('.', 'www', 'gdocs_meta2.xsl') 
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

def tidy_and_premail(content):
    return content
    # from tidylib import tidy_document
    # from xhtmlpremailer import xhtmlPremailer
    
   	## Tidy the HTML
    
    # beautifulHtmlString, errors = tidy_document(content,
		# options={
		# 'output-xhtml': 1,     # XHTML instead of HTML4
		# 'indent': 0,           # Don't use indent, add's extra linespace or linefeeds which are big problems
		# 'tidy-mark': 0,        # No tidy meta tag in output
		# 'wrap': 0,             # No wrapping
		# 'alt-text': '',        # Help ensure validation
		# 'doctype': 'strict',   # Little sense in transitional for tool-generated markup...
		# 'force-output': 1,     # May not get what you expect but you will get something
		# 'numeric-entities': 1, # remove HTML entities like e.g. nbsp
		# 'clean': 1,            # remove
		# 'bare': 1,
		# 'word-2000': 1,
		# 'drop-proprietary-attributes': 1,
		# 'enclose-text': 1,     # enclose text in body always with <p>...</p>
		# 'logical-emphasis': 1  # transforms <i> and <b> text to <em> and <strong> text
		# })
        
	## Move CSS from Stylesheet inside the tags
	# p = xhtmlPremailer(beautifulHtmlString)
	# premailString = p.transform()
	# beautifulHtmlString = premailString        
    
def xsl_transform(content):
    import libxml2
    import libxslt
    
    # 1
    beautifulHtml = tidy_and_premail(content)
    
    # 2 Settings for libxml2 for transforming XHTML entities  to valid XML
    libxml2.loadCatalog(XHTML_ENTITIES)
    libxml2.lineNumbersDefault(1)
    libxml2.substituteEntitiesDefault(1)

    # 3 First transformation
    styleDoc1 = libxml2.parseFile(GDOCS2CNXML_XSL1)
    style1 = libxslt.parseStylesheetDoc(styleDoc1)
    # doc1 = libxml2.parseFile(afile))
    doc1 = libxml2.parseDoc(beautifulHtml)
    result1 = style1.applyStylesheet(doc1, None)
    #style1.saveResultToFilename(os.path.join('output', docFilename + '_meta.xml'), result1, 1)
    resultString1 = style1.saveResultToString(result1)
    style1.freeStylesheet()
    doc1.freeDoc()
    result1.freeDoc()
    
    # 4 TODO: Apply Tagsoup for creating valid XML
    
    # 5 Second transformation
    styleDoc2 = libxml2.parseFile(GDOCS2CNXML_XSL2)
    style2 = libxslt.parseStylesheetDoc(styleDoc2)
    doc2 = libxml2.parseDoc(resultString1)
    result2 = style2.applyStylesheet(doc2, None)
    #style2.saveResultToFilename('tempresult.xml', result2, 0) # just for debugging
    resultString2 = style2.saveResultToString(result2)
    style2.freeStylesheet()
    doc2.freeDoc()
    result2.freeDoc()
    
    # TODO
    # if resultDoc:
        # result = style.saveResultToString(resultDoc)
        # resultDoc.freeDoc()
    # else:
        # raise ValueError, "Unable to perform transform " + stylesheet

    return resultString2

def htmlsoup_to_cnxml(content):
    #content = addSectionTags(content)
    content = xsl_transform(content)
    #content = content.replace('xmlns="http://www.w3.org/1999/xhtml"','')
    return content

if __name__ == "__main__":
    f = open(sys.argv[1])
    content = f.read()
    print htmlsoup_to_cnxml(content)
