"""
Transform GDocs to CNXML from a Google Docs document id resource.
How a GDocs resource ID looks like:
document:someidtexthere123

"""

import zLOG
import gdata.gauth
import gdata.docs.client
from gdocs2cnxml import gdocs_to_cnxml
from gdocs_authentication import getAuthorizedGoogleDocsClient
from Products.PortalTransforms.interfaces import itransform
from config import CNXML_MIME
from helpers import GDocsImportError

class gdocs_id_to_cnxml:
    """Transform GDocs into CNXML."""
    __implements__ = itransform

    __name__ = "gdocs_id_to_cnxml"
    inputs  = ("application/xhtml+xml",)  # "text/html"
    output = CNXML_MIME

    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        # check if we have a valid import URL
        strDocKey = data
        strAuthSub = kwargs['gdocs_authsub_access_token']

        # Get a authorized Google Doce document Client
        gdClient = getAuthorizedGoogleDocsClient()
        zLOG.LOG("GDOCS2CNXML Transform", zLOG.INFO, "Login GDocs client successful.")

        # Create a AuthSub Token based on the string
        authSubToken = gdata.gauth.AuthSubToken(strAuthSub)

        # Get the entry (=document) of Google Docs
        gdEntry = gdClient.GetDoc(strDocKey, None, authSubToken)

        # Get the contents of the document
        strEntryUrl = gdEntry.content.src
        strHtml = gdClient.get_file_content(strEntryUrl, authSubToken)

        # MAIN Transformation of Google Docs HTML to CNXML
        objects = {}
        strCnxml, objects = gdocs_to_cnxml(strHtml, bDownloadImages=True)

        outdata.setData(strCnxml)
        outdata.setSubObjects(objects)

        return outdata

def register():
    return gdocs_id_to_cnxml()