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
import demjson as json
from zipfile import ZipFile
from StringIO import StringIO
import os
import zLOG

from Products.PortalTransforms.interfaces import itransform
from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLDocument import XMLService
from helpers import SWORD2RME_XSL
from helpers import SWORD_INSERT_ATTRIBUTION_XSL
from helpers import XML2JSON_XSL

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

        zLOG.LOG("Sword Transform", zLOG.INFO, "files in zip=%s" % namelist)
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
                simplified = XMLService.transform(unzipfile, SWORD2RME_XSL)
                jsonstr = XMLService.transform(simplified, XML2JSON_XSL)
                m = json.decode(jsonstr)
                zLOG.LOG("Sword Transform", zLOG.INFO, "m=%s" % m)
                meta = outdata.getMetadata()
                meta['properties'] = m
            else:
                # This is the word file
                oo_to_cnxml().convert(unzipfile, outdata, **kwargs)

        zipfile.close()
        fakefile.close()

        meta = outdata.getMetadata()
        
        # Add attribution note to the cnxml
        props = meta['properties']
        kwargs = {}
        for key in ('journal', 'year', 'url'):
          if unicode(key) in props:
            kwargs[key] = props[unicode(key)]
        
        zLOG.LOG("Sword Transform", zLOG.INFO, "attribution dict=%s" % kwargs)
        data = outdata.getData()
        if data and len(data.getvalue()) > 0:
          attributed = XMLService.transform(data, SWORD_INSERT_ATTRIBUTION_XSL, **kwargs)
          outdata.setData(StringIO(attributed))
        
        #meta['subdirs'] = subdirs.keys()

        return outdata
        
def register():
    return sword_to_folder()

