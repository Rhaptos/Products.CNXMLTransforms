"""
Transform Word or OpenOffice document to CNXML plus included images.

From OOoImportTool.

The main part of the returned idata (getData) will be the cnxml source,
and any images will be sub objects (getSubObjects).

NOTE: this is not compatible with Archetypes, which expects the data
to be the contents of the field (which is okay) but the subobjects to
be, well, subobjects of the current object. Since the CNXML module wants
siblings from the images, we have to either do it ourselves or possibly
put a dummy field on the Module itself and include the CNXML file in the
subobjects.
"""

import zipfile
import tempfile
import os
from StringIO import StringIO
import re

import zLOG
# import AccessControl
from Products.PortalTransforms.interfaces import itransform
# from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.CMFCorePermissions import View, ManagePortal

from Products.CNXMLDocument import XMLService
from Products.CNXMLDocument.CNXMLFile import autoIds

from config import CNXML_MIME
from addsectiontags import addSectionTags
from addmathml import addMathML
from helpers import symbolReplace, parseContent, parseManifest, UNICODE_DICTIONARY
from helpers import OO2CNXML_XSL, OO2OO_XSL, CNXMLTIDY_XSL, OOCONVERT, OOoImportError, harvestImportFile, moveImportFile

from rhaptos.cnxmlutils import odt2cnxml

import urllib

class oo_to_cnxml:
    """Transform OOo Writer or MS Word documents into CNXML and associated embedded images."""
    __implements__ = itransform

    __name__ = "oo_to_cnxml"
    inputs  = ("application/msword", "application/vnd.sun.xml.writer")   # for OOo 2.0:  application/vnd.oasis.opendocument.text  
    output = CNXML_MIME

    config = {
        'server_address':'localhost:2002',
        'harvest_dir_success':'',
        'harvest_dir_failure':'',
        'import_pagecount_limit':'40',
    }
    config_metadata = {
        'server_address':('string', 'Server address', 'Address and port of running OpenOffice server',),
        'harvest_dir_success':('string', 'Successful harvest directory', 'Directory where successful import files are saved.',),
        'harvest_dir_failure':('string', 'Failure harvest directory', 'Directory where files, which could not be successfully imported, are saved.',),
        'import_pagecount_limit':('string', 'Page count limit', 'Word Import page count limit',),
    }

    ## helper methods

    def writeToGood(self,binData,strUser,strOriginalFileName):
        bSaveToTemp = True
        bHarvestingOn = ( len(self.config['harvest_dir_success']) > 0 )
        # zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "bHarvestingOn is %s" % bHarvestingOn)
        (strHead, strTail) = os.path.split(strOriginalFileName)
        (strRoot, strExt)  = os.path.splitext(strTail)

        if bHarvestingOn:
            strHarvestDirectory = self.config['harvest_dir_success']
            # zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Harvested directory: " + strHarvestDirectory)
            (strHarvestDirectory,strFileName) = harvestImportFile(binData,strHarvestDirectory,strOriginalFileName,strUser)
            if len(strFileName) > 0:
                bSaveToTemp = False
                strFileName = strHarvestDirectory + strFileName
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Harvested imported Word doc: " + strFileName)
            else:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to harvest imported Word doc " + strOriginalFileName + " to directory " + strHarvestDirectory)

        if bSaveToTemp:
            strFileName = tempfile.mktemp(suffix=strExt)
            file = open(strFileName, 'w')
            file.write(binData)
            file.close()

        return strFileName

    def moveToBad(self,strFileName):
        bHarvestingOn = ( len(self.config['harvest_dir_failure']) > 0 )
        if bHarvestingOn:
            strBadHarvestDirectory = self.config['harvest_dir_failure']
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Moving: %s" % strFileName)
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "to: %s" % strBadHarvestDirectory)
            strNewFileName = moveImportFile(strFileName,strBadHarvestDirectory)
            if len(strNewFileName) == 0:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to move BAD imported Word doc: %s" % strFileName)

    def cleanup(self, strFileName):
        # if we are not harvesting the import input file, we are operating on a copy in the temp directory,
        # which needs to be removed after the import has completed.
        bHarvestingOn = ( len(self.config['harvest_dir_success']) > 0 )
        bSaveToTemp = not bHarvestingOn
        if bSaveToTemp:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Removing: %s" % strFileName)
            os.remove(strFileName)

    def convertWordToOOo(self, strFileName):
        # quote the file name to prevent shell script expansion of any
        # special characters in the file name.
        args = [OOCONVERT, "'" + strFileName + "'"]
        addr = self.config['server_address']
        if addr:
            args.append('--address')
            args.append(addr)
        pagecountlimit = self.config['import_pagecount_limit']
        if pagecountlimit:
            args.append('--pagecount')
            args.append(pagecountlimit)
        path = " ".join(args) 
        zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Invoking converter: %s" % path)

        # open pipe to ooextract

        # currently sending OpenOffice the name of the imported word file (saved locally)
        # optionally the word doc as binary could have been sent via the pipe,
        # like how the result is returned.
        # it has been speculated that the debug version of Zope/Plone on our development systems
        # prevent this.

        (i,o,e) = os.popen3(path)

        #get ooextract output
        result = o.read()

        # here is where we check to see if the input word document was too big.
        # if there is a too big documnet, stderr will have an associated message
        stderr = ''
        stderr = e.read()
        if len(stderr) > 0:
            if stderr.startswith('Error (<class uno.com.sun.star.uno.Exception'):
                # sniff out X from:
                #     Input document has X pages which exceeeds the page count limit of Y.
                if re.match('.*Input document has ', stderr):
                    msg = ''
                    msg = stderr[re.match('.*Input document has ', stderr).end():]
                    if len(msg) > 0:
                        actualpagecount = msg.split(' ')[0]
                        if actualpagecount != msg:
                            raise OOoImportError, "Input word document contains %s pages which exceeds the page count limit of %s.  The way forward (and best practice) is to divide your doccument into smaller chunks.  For reference, the page count of an average word import is about 5 pages." % (actualpagecount, pagecountlimit)

        i.close()
        o.close()
        e.close()

        return result

    ## interface methods

    def name(self):
        return self.__name__

    def toCnxml(self, strXml, objZipFile):
        # stow styles.xml in a tempfile
        styles_xml = objZipFile.read('styles.xml')
        (tmpsfile, tmpsname) = tempfile.mkstemp('.OOo')
        os.write(tmpsfile, styles_xml)
        os.close(tmpsfile)
        stylesPath=tmpsname

        #
        # not strictly required.  this xform removes empty paragraphs.
        # makes other oo 2 cnxml xforms possible.
        #
        try:
            strOOoXml = XMLService.transform(strXml, OO2OO_XSL, stylesPath=stylesPath)
            if len(strOOoXml) == 0:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "OOo to OOo XSL transform failed.");
                strOOoXml = strXml
        except:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "OOo to OOo XSL transform failed.");
            strOOoXml = strXml

        # Clean up styles.xml tempfile
        os.remove(tmpsname)

        #
        # addSectionTags() calls the SAX parser.parse() which expects a file argument
        # thus we force the xml string into being a file object
        #
        try:
            strSectionedXml = addSectionTags(StringIO(strOOoXml))
            if len(strSectionedXml) > 0:
                bAddedSections = True
            else:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to add sections.");
                strSectionedXml = strOOoXml
                bAddedSections = False
        except:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to add sections.");
            strSectionedXml = strOOoXml
            bAddedSections = False

        #
        # add external MathML as child of <draw:object> via SAX parser.
        #
        try:
            strMathedXml = addMathML(StringIO(strSectionedXml), objZipFile)
            if len(strMathedXml) > 0:
                bAddedMath = True
            else:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to add MathML.");
                strMathedXml = strSectionedXml
                bAddedMath = False
        except:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Failed to add MathML.");
            strMathedXml = strSectionedXml
            bAddedMath = False

        #
        # oo 2 cnxml via xsl transform.
        #
        try:
            strCnxml = XMLService.transform(strMathedXml, OO2CNXML_XSL)
            bTransformed = True
        except:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "OOo to CNXML XSL transform failed.");
            # set strCnxml to invalid CNXML ...
            strCnxml = '<>'
            bTransformed = False

        #
        # Replace Word Symbol Font with correct entity
        #
        strCnxml = symbolReplace(strCnxml, UNICODE_DICTIONARY)

        #
        # Global id generation
        #
        strCnxml = autoIds(strCnxml, prefix='oo-')

        #
        # Error handling
        #
        errors = XMLService.validate(strCnxml)
        if errors:

            if bAddedSections or bAddedMath:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Invalid CNXML generated. Trying w/o sections and MathML. Errors were \n" + str([str(e) for e in errors]))

                try:
                    strCnxml = XMLService.transform(strXml, OO2CNXML_XSL)
                    strCnxml = autoIds(strCnxml, prefix='oo-')
                except:
                    zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "OOo to CNXML XSL transform failed again with the undoctored OOo Xml.");
                    strCnxml = '<>'

                errors = XMLService.validate(strCnxml)
                if errors:
                    zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Still...invalid CNXML. errors were \n" + str(errors))
                    raise OOoImportError, "Generated CNXML is invalid"
            else:
                zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Invalid CNXML generated. errors were \n" + str(errors))
                raise OOoImportError, "Generated CNXML is invalid"

        #
        # Tidy up the CNXML
        #
        docCnxmlClean = XMLService.transform(strCnxml, CNXMLTIDY_XSL)

        return str(docCnxmlClean)

    def convert(self, data, outdata, **kwargs):
        ### JCC TODO: all the back and forth about whether the data is a
        ###           file or data should be streamlined, if possible

        strOriginalFileName = kwargs['original_file_name']
        strUserName = kwargs['user_name']
        zLOG.LOG("OOo2CNXML Transform", zLOG.INFO,
                 "Original file name is : \"" + strOriginalFileName + "\". User is : \"" + strUserName + "\"")

        # write the file to disk; attempt to harvest to central location else put in /tmp
        strFileName = self.writeToGood(data,strUserName,strOriginalFileName)
        if strOriginalFileName.endswith('.xml'):
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Input file is a .xml file.  Terminate import.")
            # importing .xml file sometime blows up the OOo server and lacks a use case so we punt.
            self.moveToBad(strFileName)
            raise OOoImportError, "Could not convert .xml file.  Please try another file type."

        # OOo convert a doc file into an XML file embedded in a zip file.
        try:
            binOOoData = self.convertWordToOOo(strFileName)
        except:
            self.moveToBad(strFileName)
            raise

        if len(binOOoData) == 0:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Open Office does not return anything.  The Open Office server may not be running.")
            # don't know for sure if the conversion failed, so do we leave
            # the harvested word file in the GOOD directory or do we leave
            # the word file in the BAD directory?  Choosing to keep the GOOD
            # as pristine as possible at the current time.
            self.moveToBad(strFileName)
            raise OOoImportError, "Could not convert file"

        try:
            fileOOo = StringIO(binOOoData)
            #zipfileob = zipfile.ZipFile(fileOOo, 'rb')
        except zipfile.BadZipfile:
            zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Open Office returns something besides the expected zip file.")
            # don't know for sure if the conversion failed, so we leave
            # the harvested word file in the GOOD directory.
            raise OOoImportError, "Could not convert file"

        # massage OOo XML and do a XSL transform to produce CNXML
        #strOOoXml = zipfileob.read('content.xml')

        #if len(strOOoXml) == 0:
        #    zLOG.LOG("OOo2CNXML Transform", zLOG.INFO, "Open Office does not return the expected XML.  Open Office may have failed in converting the input Word document into its native file XML format.")
        #    self.moveToBad(strFileName)
        #    raise OOoImportError, "Could not convert file"

        try:
            #strCnxml = self.toCnxml(strOOoXml, zipfileob)
            elCnxml, filesDict, errors = odt2cnxml.transform(fileOOo)
            from lxml import etree
            strCnxml = etree.tostring(elCnxml, pretty_print=True)
        except OOoImportError:
            # toCnxml() wrote log messages
            self.moveToBad(strFileName)
            raise OOoImportError, "Generated CNXML is invalid"

        fileCnxmlClean = StringIO(strCnxml)
        outdata.setData(fileCnxmlClean)

        # Add images
        objects = filesDict #{}
        outdata.setSubObjects(objects)

        self.cleanup(strFileName)

        return outdata

def register():
    return oo_to_cnxml()
