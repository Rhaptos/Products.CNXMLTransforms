"""
Transform  Rhaptos-acceptable CNXML to Authentic-generated CNXML.

The main part of the returned idata (getData) will be the cnxml source,
and any images will be sub objects (getSubObjects). However, since the
input is XML, no images are expected.

NOTE: see OOoTransform header about compatibility with Archetypes fields.
"""
from zope.interface import implements

from Products.PortalTransforms.interfaces import itransform

from AuthenticImportExport import AuthenticImportExport

from config import CNXML_MIME

class cnxml_to_authentic:
    """Transform CNXML into Authentic CNXML."""
    implements(itransform)
    
    __name__ = "cnxml_to_authentic"
    inputs  = (CNXML_MIME,)
    output = CNXML_MIME
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        importer = AuthenticImportExport()
        text = importer.exportFile(data)
        outdata.setData(text)
        # nothing to do for outdata.setSubObjects(objects)
        return outdata

def register():
    return cnxml_to_authentic()
