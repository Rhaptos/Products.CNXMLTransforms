"""
Transform a Sword Zip file to CNXML module.

The main part of the returned idata (getData) will be the
index.cnxml file. The sub objects (getSubObjects) will be
the other objects in the module, which should be siblings to
the CNXML file.

Parameter 'data' is expected to be a binary zipfile. The contents
will be a Word file and a mets.xml file

Not certified for nested contents.

NOTE: see OOoTransform header about compatibility with Archetypes fields.
"""

from zipfile import ZipFile
from StringIO import StringIO
import os
import zLOG

from Products.PortalTransforms.interfaces import itransform
from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLDocument import XMLService
from helpers import SWORD2MDML_XSL

class sword_to_folder:
    """Transform zip file to RhaptosModuleEditor with contents."""
    __implements__ = itransform
    
    __name__ = "sword_to_folder"
    inputs  = ("application/zip",)
    output = "application/cmf+folderish"
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        """Input is a zip file. Output is idata, with getData being index.cnxml and subObjects being other siblings."""
        fakefile = StringIO(data)
        zipfile = ZipFile(fakefile, 'r')
        
        prefix = ''
        namelist = zipfile.namelist()
        lenlist = len(namelist)
        if lenlist > 1:
            prefix = os.path.commonprefix(namelist)
            lastslash = prefix.rfind("/")
            if lastslash != -1: prefix = prefix[:lastslash+1]
            else: prefix = ''
        elif lenlist == 1:
            name = namelist[0]
            lastslash = name.rfind("/")
            if lastslash != -1: prefix = name[:lastslash+1]

        for name in namelist:
            modname = name[len(prefix):]
            if not modname:               # some zip programs show directories by themselves
              continue
            isubdir = modname.find('/')
            if isubdir != -1:             # subdirs, incl. especially 'stylesheets', not imported
              continue
            unzipfile = zipfile.read(name)
            if modname == "mets.xml":
                zLOG.LOG("Sword Transform", zLOG.INFO, "starting...")
                mdml = XMLService.transform(unzipfile, SWORD2MDML_XSL)
                zLOG.LOG("Sword Transform", zLOG.INFO, "mdml=%s" % mdml)
                doc = XMLService.parseString(mdml)
                zLOG.LOG("Sword Transform", zLOG.INFO, "doc=%s" % doc)
                nsMapping = { "md": "http://cnx.rice.edu/mdml/0.4" }
                ctxt = XMLService.createContext(doc, nsMapping)
                zLOG.LOG("Sword Transform", zLOG.INFO, "ctxt=%s" % ctxt)
                meta = outdata.getMetadata()
                meta['title'] = XMLService.xpathString(ctxt, '//*[local-name()="title"]/text()')
                meta['abstract'] = XMLService.xpathString(ctxt, '//*[local-name()="abstract"]/text()')

                meta['keywords'] = []
                for n in XMLService.xpathEval(ctxt, '//*[local-name()="keyword"]/text()'):
                    meta['keywords'].append(XMLService.nodeValue(n))

                zLOG.LOG("Sword Transform", zLOG.INFO, "mets.xml 2 mdml=%s" % mdml)
            else:
                # This is the word file
                oo_to_cnxml().convert(unzipfile, outdata, **kwargs)

        zipfile.close()
        fakefile.close()

        meta = outdata.getMetadata()
        #meta['subdirs'] = subdirs.keys()

        return outdata
        
def register():
    return sword_to_folder()

