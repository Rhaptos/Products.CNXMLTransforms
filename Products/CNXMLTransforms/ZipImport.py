"""
Transform Zip file to CNXML module.

The main part of the returned idata (getData) will be the
index.cnxml file. The sub objects (getSubObjects) will be
the other objects in the module, which should be siblings to
the CNXML file.

Parameter 'data' is expected to be a binary zipfile. The contents
can be directly in the zipfile (as IMSExport does) or in a
single container folder (as ZipExport does).

Could probably easily duplicate this with tarfile.TarFileCompat:
see dist_plone for example.

Could also easily be configured for other types, or even a selectable type.

Not certified for nested contents.

NOTE: see OOoTransform header about compatibility with Archetypes fields.
"""

from zipfile import ZipFile
from StringIO import StringIO
import os

from Products.PortalTransforms.interfaces import itransform

class zip_to_folder:
    """Transform zip file to RhaptosModuleEditor with contents."""
    __implements__ = itransform
    
    __name__ = "zip_to_folder"
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

        subdirs = {}
        ignored = []
        objects = {}
        for name in namelist:
            modname = name[len(prefix):]
            if not modname:               # some zip programs show directories by themselves
              continue
            isubdir = modname.find('/')
            if isubdir != -1:             # subdirs, incl. especially 'stylesheets', not imported
              subdir = modname[:isubdir]
              if not subdirs.has_key(subdir): subdirs[subdir] = 1
              continue
            ## disabled until we get a better handle on "viewable" export...
            #if modname == 'index.xhtml':  # do not import index.xhtml
            #  ignored.append('index.xhtml')
            #  continue
            ## probably also do the same with README
            unzipfile = zipfile.read(name)
            if modname == "index.cnxml":
                if unzipfile:
                    outdata.setData(unzipfile)
                else:
                    ignored.append('index.cnxml')
            else:
                objects[modname] = unzipfile

        zipfile.close()
        fakefile.close()

        meta = outdata.getMetadata()
        meta['subdirs'] = subdirs.keys()
        meta['ignored'] = ignored

        outdata.setSubObjects(objects)
        return outdata
        
def register():
    return zip_to_folder()        