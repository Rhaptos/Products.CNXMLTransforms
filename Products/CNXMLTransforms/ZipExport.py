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
from Products.RhaptosModuleStorage.ModuleView import ModuleView
from Products.CMFCore.utils import getToolByName

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("ZipExport: ", severity, msg)

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
        if isinstance(data, ModuleView):
            modview = data
            module_id = modview.objectId
            module_version = modview.id == 'latest' and modview.version or modview.id
            containername = "%s_%s" % (module_id,module_version)
            # containername = data.absolute_url(relative=1)
            content, zipfile = makeModuleViewZip(data, containername)
        else:
            containername = data.getId().replace('.','-')
            content, zipfile = makeZipFile(data, containername)

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

def makeModuleViewZip(data, containername=""):
    """ Add files from published module to zip file.
    Parameters:
        data - the ModuleView object for the published module
        containername - the location of the module, usually latest
    """
    content = StringIO()
    zipfile = ZipFile(content, 'w', ZIP_DEFLATED)
    zipfile = _makeModuleViewZip(data, zipfile, containername)
    return (content, zipfile)

def _makeModuleViewZip(data, zipfile, containername=""):
    """ Add files from published module to zip file.
    Parameters:
        data - the ModuleView object for the published module
        zipfile - the zip file to add module files to
        containername - the location of the module, usually latest
    """
    if containername: containername = "%s/" % containername       # '/' is okay instead of os.sep, since it's going into zipfile

    fileNames = data.objectIds()
    for obj in fileNames:
        file = data.getFile(obj)
        path = "%s%s" % (containername, obj)
        zipfile.writestr(path, str(file))

    # Handle CNXML version upgrade
    cnxml = data.getDefaultFile()
    if not cnxml.upgrade():
        cnxml.setMetadata()
    module_file_name = 'index_auto_upgrade.cnxml'
    file_location = "%s%s" % (containername,module_file_name)
    if type(cnxml.data) == type(u''):
        cdata = str(cnxml.data.encode('utf-8'))
    else:
        cdata = str(cnxml.data)
    zipfile.writestr(file_location, cdata)

    return zipfile
