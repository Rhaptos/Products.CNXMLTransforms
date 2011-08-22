#! /usr/bin/env python
import sys
import os
import urllib2
#from urlparse import urlparse
import subprocess
from Globals import package_home
import libxml2
import libxslt
from tidylib import tidy_document
from xhtmlpremailer import xhtmlPremailer
from lxml import etree
import magic

XHTML_ENTITIES = os.path.join(package_home(globals()), 'www', 'catalog_xhtml', 'catalog.xml')
HTMLSOUP2CNXML_XSL = os.path.join(package_home(globals()), 'www', 'xhtml2cnxml_meta.xsl')

# Tidy up the Google Docs HTML Soup
def tidy_and_premail(content):
    # HTML Tidy
    strTidiedHtml, strErrors = tidy_document(content, options={
        'output-xhtml': 1,     # XHTML instead of HTML4
        'indent': 0,           # Don't use indent, add's extra linespace or linefeeds which are big problems
        'tidy-mark': 0,        # No tidy meta tag in output
        'wrap': 0,             # No wrapping
        'alt-text': '',        # Help ensure validation
        'doctype': 'strict',   # Little sense in transitional for tool-generated markup...
        'force-output': 1,     # May not get what you expect but you will get something
        'numeric-entities': 1, # remove HTML entities like e.g. nbsp
        'clean': 1,            # remove
        'bare': 1,
        'word-2000': 1,
        'drop-proprietary-attributes': 1,
        'enclose-text': 1,     # enclose text in body always with <p>...</p>
        'logical-emphasis': 1  # transforms <i> and <b> text to <em> and <strong> text
        })

	# Move CSS from stylesheet inside the tags with. BTW: Premailer do this usually for old email clients.
    # Use a special XHTML Premailer which does not destroy the XML structure.
    premailer = xhtmlPremailer(strTidiedHtml)
    strTidiedPremailedHtml = premailer.transform()
    return strTidiedPremailedHtml

# Main method. Doing all steps for the HTMLSOUP to CNXML transformation
def xsl_transform(content, bDownloadImages):
    # 1
    strTidiedHtml = tidy_and_premail(content)

    # 2 Settings for libxml2 for transforming XHTML entities  to valid XML
    libxml2.loadCatalog(XHTML_ENTITIES)
    libxml2.lineNumbersDefault(1)
    libxml2.substituteEntitiesDefault(1)

    # 3 First XSLT transformation
    styleDoc1 = libxml2.parseFile(HTMLSOUP2CNXML_XSL)
    style1 = libxslt.parseStylesheetDoc(styleDoc1)
    # doc1 = libxml2.parseFile(afile))
    doc1 = libxml2.parseDoc(strTidiedHtml)
    result1 = style1.applyStylesheet(doc1, None)
    #style1.saveResultToFilename(os.path.join('output', docFilename + '_meta.xml'), result1, 1)
    strResult1 = style1.saveResultToString(result1)
    style1.freeStylesheet()
    doc1.freeDoc()
    result1.freeDoc()

#    # Second transformation
#    styleDoc2 = libxml2.parseFile(GDOCS2CNXML_XSL2)
#    style2 = libxslt.parseStylesheetDoc(styleDoc2)
#    doc2 = libxml2.parseDoc(strXml)
#    result2 = style2.applyStylesheet(doc2, None)
#    #style2.saveResultToFilename('tempresult.xml', result2, 0) # just for debugging
#    strResult2 = style2.saveResultToString(result2)
#    style2.freeStylesheet()
#    doc2.freeDoc()
#    result2.freeDoc()

    return strResult1

def htmlsoup_to_cnxml(content):
    content = xsl_transform(content)
    return content

if __name__ == "__main__":
    f = open(sys.argv[1])
    content = f.read()
    print htmlsoup_to_cnxml(content)
