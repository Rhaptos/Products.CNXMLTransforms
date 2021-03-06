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
from DateTime import DateTime
import os
from Products.CNXMLDocument import XMLService
from helpers import MDML2JSON_XSL
import demjson


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
        mdata = {}
        preflen = len(prefix)
        for name in namelist:
            modname = name[preflen:]
            if not modname:               # some zip programs store directories by themselves
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
            if modname == 'index_auto_generated.cnxml':  # do not import autogenerated cnxml
              ignored.append('index_auto_generated.cnxml')
              continue
            unzipfile = zipfile.read(name)
            if modname == "index.cnxml":
                if unzipfile:
                    outdata.setData(unzipfile)
                    # Parse out the mdml for trusted import
                    jsonstr = XMLService.transform(unzipfile, MDML2JSON_XSL)
                    metadict = demjson.decode(jsonstr)

                    # First, direct copies
                    for k in ('abstract','title','language'):
                        val = metadict.get(k)
                        if type(val) == type(u''):
                            val = val.encode('UTF-8')
                        if not(val):
                            val = ''
                        mdata[k] = val

                    # Now, unwrap one level of dict for lists
                    for k in ('subjectlist','keywordlist'):
                        listdict = metadict.get(k)
                        if listdict:
                            lkey = listdict.keys()[0] # should only be one
                            mlist = listdict[lkey]
                            if isinstance(mlist,basestring):
                                listdict[lkey] = [mlist]
                            mdata.update(listdict)

                    # Rename
                    if metadict.has_key('content-id'):
                        mdata['objectId'] = metadict['content-id'].encode('UTF-8')
                    if metadict.has_key('license'):
                        if metadict['license'].has_key('url'):
                            mdata['license'] = metadict['license']['url'].encode('UTF-8')
                        else:
                            mdata['license'] = metadict['license']['href'].encode('UTF-8')

                    # DateTime strings
                    for k in ('created','revised'):
                        if metadict.has_key(k):
                            mdata[k] = DateTime(metadict[k])

                    # And the trickiest, unwrap and split roles (userids must be str, not unicode)
                    if metadict.has_key('roles'):
                        mdata.update(dict([(r['type']+'s',str(r['_text']).split()) for r in metadict['roles']['role']]))
                        #FIXME need to do collaborators here, as well - untested below
                        mdata['collaborators'] = {}.fromkeys(' '.join([r['_text'] for r in metadict['roles']['role']]).encode('UTF-8').split()).keys()
                else:
                    ignored.append('index.cnxml')
            else:
                objects[modname] = unzipfile

        zipfile.close()
        fakefile.close()

        meta = outdata.getMetadata()
        meta['subdirs'] = subdirs.keys()
        meta['ignored'] = ignored
        meta['metadata'] = mdata

        outdata.setSubObjects(objects)
        return outdata
        
def register():
    return zip_to_folder()        
