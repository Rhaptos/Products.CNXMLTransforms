"""
Transform CNXML module to Zip file with all module contents.

The main part of the returned idata (getData) will be zip file,
suitable for downloading. The sub objects (getSubObjects) will
be unused.

Note that 'data' is expected to be a RhaptosModuleEditor object,
which is unusual. Probably not intended, but it'll work.

Could probably easily duplicate this with tarfile.TarFileCompat:
see dist_plone for example.

Not recursive! Only deals with one level.
"""

from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO

from Products.PortalTransforms.interfaces import itransform

class folder_to_zip:
    """Transform RhaptosModuleEditor (or any other portal-folderish object!) to Zip file of its contents."""
    __implements__ = itransform
    
    __name__ = "folder_to_zip"
    inputs  = ("application/cmf+folderish",)
    output = "application/zip"
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        """Input is a content folderish object. Output is idata, but getData returns a binary zip file."""
        content, zipfile = makeZipFile(data, data.getId().replace('.','-'))
        
        zipfile.close()
        outdata.setData(content.getvalue())
        content.close()
        # nothing to do for outdata.setSubObjects(objects)
        return outdata
        
def register():
    return folder_to_zip()
    
class NoWrite(Exception): pass

def makeZipFile(data, containername="", getContent=('getSource','manage_FTPget','__str__'), callback=None):
    """Return a tuple of (StringIO, zipfile) of the visible first-level contents of 'data'.
    To put contents in a container (instead of unzipping in a big pile), supply a 'containername'.
    Tries attributes or methods from 'getContent', in order, to get file contents from objects.
    The function 'callback' will be called on every included file, like so: 'callback(name, path, obj)';
    if it throws a NoWrite exception, the object is not included in the zip file.
    
    Caller must close both zipfile and StringIO return objects.
    
    Note: NOT recursive! We don't need that yet.
    """
    content = StringIO()
    zipfile = ZipFile(content, 'w', ZIP_DEFLATED)
    if containername: containername = "%s/" % containername       # '/' is okay instead of os.sep, since it's going into zipfile

    for obj in data.listFolderContents(suppressHiddenFiles=True):
        name = obj.getId()
        getRepr = None
        for m in getContent:
            getRepr = getattr(obj, m, None)
            if getRepr: break

        if getRepr:
            if callable(getRepr):
                val = getRepr()
            else:
                val = getRepr
            if not val: val = ''
            path = "%s%s" % (containername, name)
            try:
              if callback: callback(name, path, obj)
              zipfile.writestr(path, str(val))
            except NoWrite:
              pass

    return (content, zipfile)
