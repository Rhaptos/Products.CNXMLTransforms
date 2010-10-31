"""
Transform CNXML module to IMS Content file with all module contents.

The main part of the returned idata (getData) will be zip file,
suitable for downloading. The sub objects (getSubObjects) will
be unused.

Note that 'data' is expected to be a RhaptosModuleEditor object,
which is unusual. Probably not intended, but it'll work.

NOTE: see OOoImport header about compatibility with Archetypes fields.

NOTE: we could also do this for courses.

NOTE: currently packages CNXML. HTML would be good. Need an XHTMLExport first.
"""
from zope.interface import implements

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import itransform

from Products.RhaptosContent import MODULE_XSL

from config import GLOBALS
from ZipExport import makeZipFile

MANIFEST = "imsmanifest.xml"
IDENTIFIER = "Rhaptos-Module-%s"

class folder_to_ims:
    """Transform RhaptosModuleEditor (or any other portal-folderish object!) to Zip file of its contents."""
    implements(itransform)
    
    __name__ = "folder_to_ims"
    inputs  = ("application/cmf+folderish",)
    output = "application/zip"
        
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        """Input is a content folderish object. Output is idata, but getData returns a binary zip file."""
        
        # construct manifest file structure
        obj = data.getPublishedObject()
        if not obj: obj = data               # this needs to be smarter for non-pub objects
        identity = IDENTIFIER % obj.absolute_url()

        manifestzpt = PageTemplateFile('www/ieeemd', GLOBALS)
        manifestzpt.content_type = "text/xml"
        manifestzpt.title = "Manifest Template"
        manifestzpt = manifestzpt.__of__(data)
        
        # set up metadata info
        modmeta = data.getMetadata()
        moduledata = {}
        moduledata["modulename"] = data.getId()
        moduledata["url"] = (data.getPublishedObject() or data).absolute_url()
        moduledata["title"] = modmeta['title']
        moduledata["description"] = modmeta['abstract']
        owners = ()
        for x in modmeta['licensors']:
            owners = owners + (getUserFullname(data, x),)
        moduledata["rights"] = "This module is copyright %s under the license: %s" % (", ".join(owners), modmeta['license'])
        moduledata["size"] = data.get_size()
        moduledata["mime"] = "application/cnxml+xml"
        moduledata["language"] = 'en'
        #moduledata["userlanguage"] = 'en'
        moduledata["keywords"] = modmeta['keywords']
        moduledata["version"] = modmeta['version']
        moduledata["status"] = data.state in ("created", "modified") and "draft" or "final"
        contributors = ()
        for x in modmeta['authors']:
            vcard = getUserVCard(data, x)
            contributors = contributors + ({"role":"author", "entity":vcard},)  # also date, but we don't support that
        for x in modmeta['maintainers']:
            vcard = getUserVCard(data, x)
            contributors = contributors + ({"role":"editor", "entity":vcard},)  # also date, but we don't support that
        moduledata["contributors"] = contributors
        #moduledata["interactive"] = 0  # how do we figure this?
        # future: references (links), annotations, classifications (taxonomy)
        moduledata["files"] = []

        def addToResource(name, path, obj):
            moduledata["files"].append(path)
        
        container = data.getId().replace('.','-')
        content, zipfile = makeZipFile(data, container, callback=addToResource)
        
        ## disable XHTML export until we have a better handle on what it looks like
        #source = data.module_export_template(**kw)
        #text = data.cnxml_transform(source, stylesheet=MODULE_XSL)
        #zipfile.writestr('%s/index.xhtml' % container, text)

        manifest = manifestzpt(**moduledata)
        zipfile.writestr(MANIFEST, manifest)

        zipfile.close()
        outdata.setData(content.getvalue())
        content.close()
        # nothing to do for outdata.setSubObjects(objects)
        return outdata
        
def register():
    return folder_to_ims()

def getUserFullname(context, userid):
    """Return a full name string for a given user, based on memberdata properties.
    Must be given a context as well as an id so that it can look up the tool.
    """
    mship = getToolByName(context, 'portal_membership')
    m = mship.getMemberById(userid)
    
    honorific = m.getProperty('honorific', '')
    firstname = m.getProperty('firstname', '')
    othername = m.getProperty('othername', '')
    surname = m.getProperty('surname', '')
    lineage = m.getProperty('lineage', '')
    
    return " ".join([n for n in (honorific, firstname, othername, surname, lineage) if n])

def getUserVCard(context, userid):
    """Return a vCard string for a given user, based on memberdata properties.
    Must be given a context as well as an id so that it can look up the tool.
    """
    mship = getToolByName(context, 'portal_membership')
    m = mship.getMemberById(userid)
    
    email = m.getProperty('email', '')
    honorific = m.getProperty('honorific', '')
    firstname = m.getProperty('firstname', '')
    othername = m.getProperty('othername', '')
    surname = m.getProperty('surname', '')
    lineage = m.getProperty('lineage', '')
    homepage = m.getProperty('homepage', '')
    fullname = " ".join([n for n in (honorific, firstname, othername, surname, lineage) if n])
    
    vCard = ["BEGIN:VCARD","VERSION:2.1"]
    vCard.append("FN:%s" % fullname)
    vCard.append("N:%s" % ";".join((surname, firstname, othername, honorific, lineage)))
    vCard.append("EMAIL:%s" % email)
    if homepage: vCard.append("URL:%s" % homepage)
    vCard.append("END:VCARD")
    
    return "\n".join(vCard)
