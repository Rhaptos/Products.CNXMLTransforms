
from Products.CMFCore.utils import getToolByName

def install(portal):
    portal_setup = getToolByName(portal, 'portal_setup')
    import_context = portal_setup.getImportContextID()
    portal_setup.setImportContext(
            'profile-Products.CNXMLTransforms:default')
    portal_setup.runAllImportSteps()
    portal_setup.setImportContext(import_context)

def uninstall(portal):
    portal_setup = getToolByName(portal, 'portal_setup')
    import_context = portal_setup.getImportContextID()
    portal_setup.setImportContext(
            'profile-Products.CNXMLTransforms:uninstall')
    portal_setup.runAllImportSteps()
    portal_setup.setImportContext(import_context)

