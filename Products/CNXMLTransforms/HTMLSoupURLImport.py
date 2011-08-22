"""
Transform HTML Soup to CNXML from URL.

"""

import zLOG
from Products.PortalTransforms.interfaces import itransform
from htmlsoup2cnxml import htmlsoup_to_cnxml as htmlsoupConverter
from config import CNXML_MIME
from helpers import HTMLSoupImportError

class htmlsoup_url_to_cnxml:
    """Transform HTML soup into CNXML."""
    __implements__ = itransform
    
    __name__ = "htmlsoup_url_to_cnxml"
    inputs  = ("application/xhtml+xml",)  # "text/html"
    output = CNXML_MIME
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        text = htmlsoupConverter(data)
        outdata.setData(text)
        # nothing to do for outdata.setSubObjects(objects)
        return outdata
    
def register():
    return htmlsoup_url_to_cnxml()