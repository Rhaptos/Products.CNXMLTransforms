"""
Transform Authentic-generated CNXML to Rhaptos-acceptable CNXML.

The main part of the returned idata (getData) will be the cnxml source,
and any images will be sub objects (getSubObjects). However, since the
input is XML, no images are expected.

NOTE: see OOoImport header about compatibility with Archetypes fields.
"""

from Products.PortalTransforms.interfaces import itransform

from AuthenticImportExport import AuthenticImportExport

from config import CNXML_MIME

class authentic_to_cnxml:
    """Transform Authentic CNXML into CNXML."""
    __implements__ = itransform
    
    __name__ = "authentic_to_cnxml"
    inputs  = (CNXML_MIME,)
    output = CNXML_MIME
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        importer = AuthenticImportExport()
        text = importer.importFile(data)
        outdata.setData(text)
        # nothing to do for outdata.setSubObjects(objects)
        return outdata

def register():
    return authentic_to_cnxml()