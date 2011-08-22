"""
Transform GDocs to CNXML from file.

"""

import zLOG
from Products.PortalTransforms.interfaces import itransform
from gdocs2cnxml import gdocs_to_cnxml as gdocsConverter
from config import CNXML_MIME
from helpers import GDocsImportError

class gdocs_file_to_cnxml:
    """Transform GDocs into CNXML."""
    __implements__ = itransform
    
    __name__ = "gdocs_file_to_cnxml"
    inputs  = ("application/xhtml+xml",)  # "text/html"
    output = CNXML_MIME
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        text = gdocsConverter(data)
        outdata.setData(text)
        # nothing to do for outdata.setSubObjects(objects)
        return outdata
    
def register():
    return gdocs_file_to_cnxml()