"""
Transform GDocs to CNXML from URL.

"""

import re
import zLOG
import gdata.gauth
import gdata.docs.client
from gdocs2cnxml import gdocs_to_cnxml
from gdocs_authentication import getAuthorizedGoogleDocsClient
from Products.PortalTransforms.interfaces import itransform
from config import CNXML_MIME
from helpers import GDocsImportError

class gdocs_url_to_cnxml:
    """Transform GDocs into CNXML."""
    __implements__ = itransform

    __name__ = "gdocs_url_to_cnxml"
    inputs  = ("application/xhtml+xml",)  # "text/html"
    output = CNXML_MIME

    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        # check if we have a valid import URL
        strImportUrl = data
        # Get the Google Docs ID from the URL with regular expressions
        m = re.match(r'^.*docs\.google\.com/document/d/([^/]+).*$', strImportUrl)
        if m == None:
            raise GDocsImportError, "Import URL is not a valid Google Docs document URL."
        else:
            # get the gdocs resource id from URL
            strDocKey = 'document:' + m.group(1)

        # Get a authorized Google Doce document Client
        gdClient = getAuthorizedGoogleDocsClient()
        zLOG.LOG("GDOCS2CNXML Transform", zLOG.INFO, "Login GDocs client successful.")

        # Get the entry (=document) of Google Docs
        gdEntry = gdClient.GetDoc(strDocKey)  # , None, auth_sub_token

        # Get the contents of the document
        strEntryUrl = gdEntry.content.src
        strHtml = gdClient.get_file_content(strEntryUrl) # , auth_sub_token

        # MAIN Transformation of Google Docs HTML to CNXML
        objects = {}
        strCnxml, objects = gdocs_to_cnxml(strHtml, bDownloadImages=True)

        outdata.setData(strCnxml)
        outdata.setSubObjects(objects)

        return outdata

def register():
    return gdocs_url_to_cnxml()