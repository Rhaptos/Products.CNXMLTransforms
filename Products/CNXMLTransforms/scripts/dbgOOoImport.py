import sys
import tidy
import zipfile
import tempfile
import os

from StringIO import StringIO
from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLTransforms.addsectiontags import addSectionTags
from Products.CNXMLTransforms.addmathml import addMathML
from Products.CNXMLTransforms.helpers import OO2OO_XSL
from Products.CNXMLTransforms.helpers import OO2CNXML_XSL
from Products.CNXMLTransforms.helpers import symbolReplace, UNICODE_DICTIONARY
from Products.CNXMLDocument import XMLService
from Products.CNXMLDocument.CNXMLFile import CNXML_AUTOID_XSL

from re import findall

#import pdb
#pdb.set_trace()

if __name__ == "__main__":
     strZipFile                     = sys.argv[1]
     strInputOOoXmlFile             = sys.argv[2]
     strOutputMassageOOoXmlFileBase = sys.argv[3]
     strOutputCnxmlFile             = sys.argv[4]
     #print 'arg1 is \n' + sys.argv[1]
     #print 'arg2 is \n' + sys.argv[2]
     #print 'arg3 is \n' + sys.argv[3]
     #print 'arg4 is \n' + sys.argv[4]

     fileInputXml = open(strInputOOoXmlFile)
     strInputOOoXml = fileInputXml.read()
     fileInputXml.close()

     strOOoXml = strInputOOoXml
     doc = XMLService.parseString(strOOoXml)

     objZipFile = zipfile.ZipFile(strZipFile, 'r') # no 'rb' since 'b' => binary?

     #
     # Pass #1 - OOo Xml to OOo Xml xform - change one entry table & remove empty <text:p>
     #
     try:
         styles_xml = objZipFile.read('styles.xml')
         (tmpsfile, tmpsname) = tempfile.mkstemp('.OOo')
         os.write(tmpsfile, styles_xml)
         os.close(tmpsfile)
         stylesPath=tmpsname

         strOutputMassageOOoXml = XMLService.transform(strOOoXml, OO2OO_XSL, stylesPath=stylesPath)
         if len(strOutputMassageOOoXml) > 0:
             print "**** suceeded in OO 2 OO XSL transform to remove empty paragraphs."
         else:
             print "**** failed in OO 2 OO XSL transform to remove empty paragraphs. return an empty string. ignore and continue.\n" + str(strErrorMsg)
             strOutputMassageOOoXml = strOOoXml

         os.remove(tmpsname)
     except XMLService.XMLParserError, strErrorMsg:
         print "**** failed in OO 2 OO XSL transform to remove empty paragraphs. raised exception. ignore and continue.\n" + str(strErrorMsg)
         strOutputMassageOOoXml = strOOoXml
         #raise

     # print "wrting to : '" + strOutputMassageOOoXmlFileBase + '.oo2oo.xml'
     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.oo2oo.xml', "w")
     fileMassagedOutputXml.write(str(strOutputMassageOOoXml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.oo2oo.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     strTidy = tidy.parseString(strOutputMassageOOoXml,**options)
     fileMassagedOutputXml.write(str(strTidy))
     fileMassagedOutputXml.close()

     strOOoXml = strOutputMassageOOoXml

     #
     # Pass #2 - add <text:section> tags via a SAX parser pass
     #
     try:
         strOutputMassageOOoXml = addSectionTags(StringIO(strOOoXml))
         if len(strOutputMassageOOoXml) > 0:
             print "**** suceeded in the SAX parser while adding sections."
         else:
             print "**** failed in the SAX parser while adding sections. return an empty string. ignore and continue."
             strOutputMassageOOoXml = strOOoXml
     except:
         print "**** failed in the SAX parser while adding sections. raised exception. ignore and continue."
         strOutputMassageOOoXml = strOOoXml
         #raise

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.sectioned.xml', "w")
     fileMassagedOutputXml.write(str(strOutputMassageOOoXml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.sectioned.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     docTidy = tidy.parseString(strOutputMassageOOoXml,**options)
     strTidy = str(docTidy)
     fileMassagedOutputXml.write(strTidy)
     #fileMassagedOutputXml.write(symbolReplace(strTidy, UNICODE_DICTIONARY))
     fileMassagedOutputXml.close()

     strOOoXml = strOutputMassageOOoXml

     #
     # Pass #3 - add MathML nodes from external OOo objects
     #
     try:
         objZipFile = zipfile.ZipFile(strZipFile, 'r')
         strOutputMassageOOoXml = addMathML(StringIO(strOOoXml), objZipFile)
         if len(strOutputMassageOOoXml) > 0:
             print "**** suceeded in the SAX parser while adding MathML."
         else:
             print "**** failed in adding MathML. return an empty string. ignore and continue."
             strOutputMassageOOoXml = strOOoXml
     except:
         print "**** failed in adding MathML. raised exception. ignore and continue."
         strOutputMassageOOoXml = strOOoXml
         #raise

     #fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '3ish', "w")
     #fileMassagedOutputXml.write(strOutputMassageOOoXml)
     #fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.mathed.xml', "w")
     fileMassagedOutputXml.write(str(strOutputMassageOOoXml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.mathed.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     docTidy = tidy.parseString(strOutputMassageOOoXml,**options)
     strTidy = str(docTidy)
     fileMassagedOutputXml.write(strTidy)
     fileMassagedOutputXml.close()

     strOOoXml = strOutputMassageOOoXml

     #doc = XMLService.parseString(strTidy)

     #
     # Pass #4 - OOo XML to CNXML xform
     #
     try:
         strOutputCnxml = XMLService.transform(strOOoXml, OO2CNXML_XSL)
         if len(strOutputCnxml) > 0:
             print "**** suceeded in OO 2 CNXML XSL transform."
         else:
             print "**** failed in OO 2 CNXML XSL transform. return an empty string. ignore and continue."
             strOutputCnxml = strOOoXml
     except:
         print "**** failed in OO 2 CNXML XSL transform. raised exception. ignore and continue."
         strOutputCnxml = strOOoXml
         #raise

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.oo2cnxml.xml', "w")
     fileMassagedOutputXml.write(str(strOutputCnxml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.oo2cnxml.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     strTidy = tidy.parseString(strOutputCnxml,**options)
     fileMassagedOutputXml.write(str(strTidy))
     fileMassagedOutputXml.close()

     #
     # Pass #5 - replace MS "private use" unicode
     #
     try:
         strCnxml = symbolReplace(strOutputCnxml, UNICODE_DICTIONARY)
         if len(strCnxml) > 0:
             print "**** suceeded in replacing MS \"private use\" unicode."
         else:
             print "**** failed in replacing MS \"private use\" unicode. return an empty string. ignore and continue."
             strCnxml = strOutputCnxml
     except:
         print "**** failed in replacing MS \"private use\" unicodes. raised exception. ignore and continue."
         strCnxml = strOutputCnxml
         #raise

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.unicode.xml', "w")
     fileMassagedOutputXml.write(str(strCnxml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.unicode.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     strTidy = tidy.parseString(strCnxml,**options)
     fileMassagedOutputXml.write(str(strTidy))
     fileMassagedOutputXml.close()

     #
     # Pass #6 - fill in missing @ids
     #
     try:
         strCnxml = XMLService.transform(strOutputCnxml, CNXML_AUTOID_XSL)
         if len(strOutputCnxml) > 0:
             print "**** suceeded in adding @id XSL transform."
         else:
             print "**** failed in adding @id XSL transform. return an empty string. ignore and continue."
             strCnxml = strOutputCnxml
     except:
         print "**** failed in adding @id XSL transform. raised exception. ignore and continue."
         strCnxml = strOutputCnxml
         #raise

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.ided.xml', "w")
     fileMassagedOutputXml.write(str(strCnxml))
     fileMassagedOutputXml.close()

     fileMassagedOutputXml = open(strOutputMassageOOoXmlFileBase + '.ided.tidy.xml', "w")
     options = dict(input_xml=1, char_encoding='utf8', indent=1)
     strTidy = tidy.parseString(strCnxml,**options)
     fileMassagedOutputXml.write(str(strTidy))
     fileMassagedOutputXml.close()

     errors = XMLService.validate(strCnxml)
     if errors:
         print "validation errors:\n" + str(errors)
     else:
         print "no validation errors."

     #raise Heck

     #
     # special carve out from OOoImport.py to facilitate
     #
     strCnxml = oo_to_cnxml().toCnxml(strInputOOoXml, objZipFile)
     errors = XMLService.validate(strCnxml)
     if errors:
         print "**** oo_to_cnxml().toCnxml() failed. does not return a valid string. Errors were \n" + str([str(e) for e in errors])
     else:
         print "**** oo_to_cnxml().toCnxml() suceeded."

     fileOutputXml = open(strOutputCnxmlFile, 'w')
     fileOutputXml.write(str(strCnxml))
     fileOutputXml.close()
