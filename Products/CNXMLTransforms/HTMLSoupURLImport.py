"""
Transform HTML Soup to CNXML from URL.

"""

import urllib2
import zLOG
from Products.PortalTransforms.interfaces import itransform
from htmlsoup2cnxml import htmlsoup_to_cnxml
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
        strUrl = data
        strHtml = urllib2.urlopen(strUrl).read()
        strCnxml = htmlsoup_to_cnxml(strHtml)
        outdata.setData(strCnxml)
        # outdata.setSubObjects(objects) # do not add subobjects now
        return outdata

def register():
    return htmlsoup_url_to_cnxml()
