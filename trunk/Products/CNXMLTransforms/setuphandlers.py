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
from Products.CNXMLTransforms.SwordImport import sword_to_folder
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
     sword_to_folder(),
)


def register_mimetypes(portal, logger):
    registry = getToolByName(portal, 'mimetypes_registry')
    logger.info('Intalling mimetypes')
    
    for mimetype in mimetypes:
        logger.info(mimetype.name())
        registry.register(mimetype)
    logger.info('done')


def deregister_mimetypes(portal, logger):
    registry = getToolByName(portal, 'mimetypes_registry')
    logger.info('Uninstalling mimetypes')
    
    for mimetype in mimetypes:
        logger.info(mimetype.name())
        registry.unregister(mimetype)
    logger.info('done')


def install_transforms(portal, logger):
    engine = getToolByName(portal, 'portal_transforms')
    logger.info('Intalling transforms')
   
    for transform in transforms:
        logger.info(transform.name())
        engine.registerTransform(transform)
    logger.info('done')
 

def uninstall_transforms(portal, logger):
    engine = getToolByName(portal, 'portal_transforms')
    logger.info('Uninstalling transforms')

    for transform in transforms:
        logger.info(transform.name())
        try:
            engine.unregisterTransform(transform.name())
        except AttributeError:
            pass
        except KeyError:
            pass
    logger.info('done')
    


def install(context):
    """Add transforms and associated mimetypes"""

    if context.readDataFile('cnxmltransforms-install.txt') is None:
        return

    logger = context.getLogger('cnxmltransforms-install')

    portal = context.getSite()
    
    # register transforms and mimetypes (order matters!)
    register_mimetypes(portal, logger)
    install_transforms(portal, logger)


def uninstall(context):
    """Custom removal"""

    if context.readDataFile('cnxmltransforms-uninstall.txt') is None:
        return

    logger = context.getLogger('cnxmltransforms-uninstall')
    portal = context.getSite()
    
    # remove transformations and mimetypes
    uninstall_transforms(portal, logger)
    deregister_mimetypes(portal, logger)
    
