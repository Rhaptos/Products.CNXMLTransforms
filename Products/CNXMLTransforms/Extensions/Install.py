from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import string


mimetypes = (
     MimeTypeItem(name="CNXML", mimetypes=("application/cnxml+xml",), extensions=("cnxml",),
                  binary="no", icon_path="text.png"),
     MimeTypeItem(name="LaTeX Zip", mimetypes=("application/zip+latex",), extensions=("zip",),
                  binary="yes", icon_path="tgz.png"),
     MimeTypeItem(name="Folderish", mimetypes=("application/cmf+folderish",), extensions=("",),
                  binary="yes", icon_path="tgz.png"),
)

#import
from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLTransforms.AuthenticImport import authentic_to_cnxml
from Products.CNXMLTransforms.XHTMLImport import xhtml_to_cnxml
from Products.CNXMLTransforms.ZipImport import zip_to_folder
from Products.CNXMLTransforms.LatexImport import latex_to_folder
#export
from Products.CNXMLTransforms.AuthenticExport import cnxml_to_authentic
from Products.CNXMLTransforms.ZipExport import folder_to_zip
from Products.CNXMLTransforms.XHTMLExport import module_to_xhtmlzip
from Products.CNXMLTransforms.IMSExport import folder_to_ims

transforms = (
     oo_to_cnxml(),
     authentic_to_cnxml(),
     xhtml_to_cnxml(),
     cnxml_to_authentic(),
     
     folder_to_zip(),
     folder_to_ims(),
     module_to_xhtmlzip(),
     zip_to_folder(),
     latex_to_folder(),
)


def register_mimetypes(portal, out):
    out.write("register mimetypes: ")
    registry = getToolByName(portal, 'mimetypes_registry')
    
    for mimetype in mimetypes:
        out.write(mimetype.name())
        registry.register(mimetype)
        out.write("... ")

    out.write("done\n")

def deregister_mimetypes(portal, out):
    out.write("deregister mimetypes: ")
    registry = getToolByName(portal, 'mimetypes_registry')
    
    for mimetype in mimetypes:
        out.write(mimetype.name())
        registry.register(mimetype)
        out.write("... ")

    out.write("done\n")

def install_transforms(portal, out):
    out.write("register transforms: ")
    engine = getToolByName(portal, 'portal_transforms')
   
    for transform in transforms:
        out.write(transform.name())
        engine.registerTransform(transform)
        out.write("... ")
 
    out.write("done\n")

def uninstall_transforms(portal, out):
    out.write("unregister transforms: ")
    engine = getToolByName(portal, 'portal_transforms')

    for transform in transforms:
        out.write(transform.name())
        try:
            engine.unregisterTransform(transform.name())
        except AttributeError:
            out.write(" (not found)")
        except KeyError:
            out.write(" (not found)")
        out.write("... ")
    
    out.write("done\n")


def install(self):
    """Add transforms and associated mimetypes"""
    out = StringIO()

    # get portal object
    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject()
    
    # Register skins
    #none
    
    # register transforms and mimetypes (order matters!)
    register_mimetypes(portal, out)
    install_transforms(portal, out)

    out.write("Installed.")
    return out.getvalue()

def uninstall(self):
    """Custom removal"""
    out = StringIO()

    # get portal object
    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject()
    
    # remove transformations and mimetypes
    uninstall_transforms(portal, out)
    deregister_mimetypes(portal, out)
    
    out.write("Uninstalled.")
    return out.getvalue()
