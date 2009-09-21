"""
Import/Export CNXMLFile to the XMLSpy/Authentic format

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import re
from Products.CNXMLDocument import XMLService

# Map namespaces onto doctype declarations (used to be in CNXMLDocument.CNXMLFile)
DTD = {
    ('http://cnx.rice.edu/cnxml',): '<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5//EN" "http://cnx.rice.edu/technology/cnxml/schema/dtd/0.5/cnxml_plain.dtd">',
    ('http://cnx.rice.edu/cnxml', 'http://www.w3.org/1998/Math/MathML'): '<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/technology/cnxml/schema/dtd/0.5/cnxml_mathml.dtd">',
    ('http://cnx.rice.edu/cnxml', 'http://cnx.rice.edu/qml/1.0'): '<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus QML//EN" "http://cnx.rice.edu/technology/cnxml/schema/dtd/0.5/cnxml_qml.dtd">',
    ('http://cnx.rice.edu/cnxml', 'http://cnx.rice.edu/qml/1.0', 'http://www.w3.org/1998/Math/MathML'): '<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML plus QML//EN" "http://cnx.rice.edu/technology/cnxml/schema/dtd/0.5/cnxml_mathml_qml.dtd">',
    }

HEADER_REGEX = re.compile("""(?P<doctype><!DOCTYPE.*?-//CNX//DTD CNXML (?P<version>[\d\.]*).*?>)\s*<[^>]*id=['"](?P<id>[^"']*)['"].*?>(?P<foot>.*)""", re.DOTALL)

XMLSPY_REGEX = re.compile("""<\?xml-stylesheet.*?http://cnx.rice.edu/cnxml/(?P<version>[^/]*)/.*?>.*?<document[^>].*?id=['"](?P<id>[^"']*)["'].*?>(?P<foot>.*)""", re.DOTALL)

XMLSPY_TEMPLATE = """<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="http://cnx.rice.edu/technology/cnxml/stylesheet/xmlspy.xsl"?>\n<?xmlspysps http://cnx.rice.edu/technology/cnxml/misc/cnxml.sps?><document xmlns="http://cnx.rice.edu/cnxml" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://cnx.rice.edu/cnxml http://cnx.rice.edu/technology/cnxml/schema/xsd/\g<version>/cnxml.xsd" id="\g<id>">\g<foot>"""

MATH_XMLSPY_TEMPLATE = """<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="http://cnx.rice.edu/technology/cnxml/stylesheet/xmlspy.xsl"?>\n<?xmlspysps http://cnx.rice.edu/technology/cnxml/misc/cnxml.sps?><document xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns="http://cnx.rice.edu/cnxml" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://cnx.rice.edu/cnxml http://cnx.rice.edu/technology/cnxml/schema/xsd/\g<version>/cnxml.xsd" id="\g<id>">\g<foot>"""

class AuthenticImportExport:

    def exportFile(self, text):
        """Convert to XMLSpy format"""
        text = XMLService.normalize(text)

        m = HEADER_REGEX.search(text)

        try:
            doctype = m.groupdict()['doctype']
        except (AttributeError, KeyError):
            raise ValueError, "Could not perform XMLSpy/Authentic export"
        
        if 'MathML' in doctype:
            template = MATH_XMLSPY_TEMPLATE
        else:
            template = XMLSPY_TEMPLATE

        try:
            export = m.expand(template)
        except (AttributeError, KeyError):
            raise ValueError, "Could not perform XMLSpy/Authentic export"
        
        return export
        

    def importFile(self, text):
        """Convert from XMLSpy format"""

        # Fixup invalid PI prefix. Naughty Altova, PIs can't start with 'xml'
        text = text.replace('<?xmlspy', '<?authentic')
        try:
            doc = XMLService.parseString(text)
        except XMLService.XMLError:
            raise ValueError, "Could not perform XMLSpy/Authentic import: unable to parse file"

        # Get rid of Authentic goop:
        xslt = doc.children
        if xslt.type != 'pi':
            doc.freeDoc()
            raise ValueError, "Could not perform XMLSpy/Authentic import: missing stylesheet PI"
        xslt.unlinkNode()
        xslt.freeNode()

        pi = doc.children
        if pi.type != 'pi':
            doc.freeDoc()
            raise ValueError, "Could not perform XMLSpy/Authentic import: missing xmlspysps PI"
        pi.unlinkNode()
        pi.freeNode()

        rootNode = doc.children
        attr = rootNode.properties
        while attr:
            if attr.name == 'schemaLocation':
                attr.removeProp()
                break
            attr = attr.next
        
        schema_ns = rootNode.removeNsDef("http://www.w3.org/2001/XMLSchema-instance")
        schema_ns.freeNode()

        ns = XMLService.listDocNamespaces(doc)
        # Get rid of namespaces we don't care about
        try:
            ns.remove('http://bibtexml.sf.net/')
            ns.remove('http://cnx.rice.edu/mdml/0.4')
        except ValueError:
            pass

        ns.sort()
        try:
            doctype = DTD[tuple(ns)]
        except KeyError:
            raise ValueError, "Cannot determine CNXML version from provided file"

        #return ns, doctype
    

        body = rootNode.serialize(encoding='utf-8')
        result = '\n'.join(['<?xml version="1.0" encoding="utf-8"?>', doctype , body])

        doc.freeDoc()

        return result

