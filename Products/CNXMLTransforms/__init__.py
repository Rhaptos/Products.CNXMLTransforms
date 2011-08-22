"""
Initialize CNXMLTransforms Product

Author: J CameronCooper
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import sys
from Products.CMFCore import utils
from AccessControl import ModuleSecurityInfo

from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLTransforms.AuthenticImport import authentic_to_cnxml
from Products.CNXMLTransforms.XHTMLImport import xhtml_to_cnxml
from Products.CNXMLTransforms.ZipImport import zip_to_folder
from Products.CNXMLTransforms.LatexImport import latex_to_folder
from Products.CNXMLTransforms.GDocsURLImport import gdocs_url_to_cnxml
from Products.CNXMLTransforms.GDocsIDImport import gdocs_id_to_cnxml
from Products.CNXMLTransforms.GDocsFileImport import gdocs_file_to_cnxml
from Products.CNXMLTransforms.HTMLSoupURLImport import htmlsoup_url_to_cnxml
from Products.CNXMLTransforms.HTMLSoupFileImport import htmlsoup_file_to_cnxml

from Products.CNXMLTransforms.AuthenticExport import cnxml_to_authentic
from Products.CNXMLTransforms.ZipExport import folder_to_zip
from Products.CNXMLTransforms.IMSExport import folder_to_ims
from Products.CNXMLTransforms.XHTMLExport import module_to_xhtmlzip

ModuleSecurityInfo('Products.CNXMLTransforms.helpers').declarePublic('OOoImportError')
ModuleSecurityInfo('Products.CNXMLTransforms.helpers').declarePublic('GDocsImportError')
ModuleSecurityInfo('Products.CNXMLTransforms.helpers').declarePublic('HTMLSoupImportError')
ModuleSecurityInfo('Products.CNXMLTransforms.helpers').declarePublic('doTransform')
ModuleSecurityInfo('Products.CNXMLTransforms.helpers').declarePublic('makeContent')

# backwards compatibility only. these names are deprecated
# may be removed in 0.5
import OOoImport
sys.modules['Products.CNXMLTransforms.OOoTransform'] = OOoImport
OOoTransform = OOoImport
import AuthenticImport
sys.modules['Products.CNXMLTransforms.AuthenticTransform'] = AuthenticImport
AuthenticTransform = AuthenticImport
import XHTMLImport
sys.modules['Products.CNXMLTransforms.XHTMLTransform'] = XHTMLImport
XHTMLTransform = XHTMLImport

def initialize(context):
    pass
