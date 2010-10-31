"""
Transform XHTML to CNXML.

The main part of the returned idata (getData) will be the cnxml source,
and any images will be sub objects (getSubObjects). However, since the
input is XML, no images are expected.

NOTE: see OOoTransform header about compatibility with Archetypes fields.
"""
from zope.interface import implements

from Products.PortalTransforms.interfaces import itransform

from html2cnxml import html_to_cnxml as xhtmlConverter
from config import CNXML_MIME

class xhtml_to_cnxml:
    """Transform XHTML into CNXML."""
    implements(itransform)
    
    __name__ = "xhtml_to_cnxml"
    inputs  = ("application/xhtml+xml",)  # "text/html"
    output = CNXML_MIME
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        text = xhtmlConverter(data)        
        outdata.setData(text)
        # nothing to do for outdata.setSubObjects(objects)
        return outdata

def register():
    return xhtml_to_cnxml()
