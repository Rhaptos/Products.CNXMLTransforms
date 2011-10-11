#------------------------------------------------------------------------------#
#   test_cnxml_transforms.py                                                   #
#                                                                              #
#       Authors:                                                               #
#       Rajiv Bakulesh Shah <raj@enfoldsystems.com>                            #
#                                                                              #
#           Copyright (c) 2009, Enfold Systems, Inc.                           #
#           All rights reserved.                                               #
#                                                                              #
#               This software is licensed under the Terms and Conditions       #
#               contained within the "LICENSE.txt" file that accompanied       #
#               this software.  Any inquiries concerning the scope or          #
#               enforceability of the license should be addressed to:          #
#                                                                              #
#                   Enfold Systems, Inc.                                       #
#                   4617 Montrose Blvd., Suite C215                            #
#                   Houston, Texas 77006 USA                                   #
#                   p. +1 713.942.2377 | f. +1 832.201.8856                    #
#                   www.enfoldsystems.com                                      #
#                   info@enfoldsystems.com                                     #
#------------------------------------------------------------------------------#
"""Unit tests.
$Id: $
"""

import os
import difflib
from Products.RhaptosTest import config
import Products.CNXMLTransforms
config.products_to_load_zcml = [('configure.zcml', Products.CNXMLTransforms),]
config.products_to_install = ['CNXMLTransforms']

from Products.RhaptosTest import base

from Products.CNXMLTransforms.helpers import doTransform

from Testing import ZopeTestCase
ZopeTestCase.installProduct('RhaptosSword')
ZopeTestCase.installProduct('CNXML')
ZopeTestCase.installProduct('UniFile')

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=['RhaptosSword'],
    extension_profiles=[
        'Products.CNXMLTransforms:default',
        'Products.UniFile:default',
        ]
    )

DIRNAME = os.path.dirname(__file__)

def diff(a, b):
    return '\n'.join(
        difflib.unified_diff(a.splitlines(), b.splitlines())
        )

class TestCNXMLTransforms(base.RhaptosTestCase):

    def afterSetUp(self):
        pass

    def _setupRhaptos(self):
        # XXX: This method needs to move to afterSetup, but afterSetup is not
        # being called for some reason.
        objectIds = self.portal.objectIds()

    def beforeTearDown(self):
        pass

    def test_latex_to_folder(self):
        self.assertEqual(1, 1)

    def test_oo_to_cnxml(self):
        self.assertEqual(1, 1)

    def test_folder_to_zip(self):
        self.assertEqual(1, 1)

    def test_zip_to_folder(self):
        self.assertEqual(1, 1)

    def test_sword_to_folder(self):
        self._setupRhaptos()
        context = self.folder
        name = "sword_to_folder"
        filename = 'module.zip'
        path = os.path.join(DIRNAME, 'data', filename)
        file = open(path, 'rb')
        data = file.read()
        file.close()
        meta = 1
        kwargs = {}

        text, subobjs, meta = doTransform(
            context, name, data, meta=1, **kwargs)
        
        returned_text = text.read()
        self.assertEqual(
            returned_text,
            no_links_reference_text,
            'The text was not extracted correctly. (%s)' % \
                diff(returned_text, no_links_reference_text)
        )

        self.assertEqual(subobjs, {}, 'There should be no sub objects.')
        self.assertEqual(
            meta, no_link_reference_meta, 'Metadata was not set correctly.')

    def test_import_new_links(self):
        self._setupRhaptos()
        context = self.folder
        name = "sword_to_folder"
        filename = 'module_with_one_featured_link.zip'
        path = os.path.join(DIRNAME, 'data', filename)
        file = open(path, 'rb')
        data = file.read()
        file.close()
        meta = 1
        kwargs = {}

        text, subobjs, meta = doTransform(
            context, name, data, meta=1, **kwargs)

        returned_text = text.read()
        self.assertEqual(
            returned_text,
            one_link_reference_text,
            'The text was not extracted correctly. (%s)' % \
                diff(returned_text, one_link_reference_text)
        )
        self.assertEqual(subobjs, {}, 'There should be no sub objects.')
        self.assertEqual(
            meta, one_link_reference_meta, 'Metadata was not set correctly.')

    def test_import_existing_links(self):
        self.fail()

    def test_import_new_and_existing_links(self):
        self.fail()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCNXMLTransforms))
    return suite


""" test data below """

no_links_reference_text = \
u'<?xml version="1.0"?>\n<document xmlns="http://cnx.rice.edu/cnxml" xmlns:md="http://cnx.rice.edu/mdml" xmlns:bib="http://bibtexml.sf.net/" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:q="http://cnx.rice.edu/qml/1.0" id="new" cnxml-version="0.7" module-id="new">\n\n<title>My first module</title>\n<metadata mdml-version="0.5">\n  <!-- WARNING! The \'metadata\' section is read only. Do not edit below.\n       Changes to the metadata section in the source will not be saved. -->\n  <md:repository>http://localhost:8080/site/content</md:repository>\n  <md:content-id>new</md:content-id>\n  <md:title>My first module</md:title>\n  <md:version>**new**</md:version>\n  <md:created>2011/10/11 10:16:37.837 GMT+2</md:created>\n  <md:revised>2011/10/11 10:16:37.957 GMT+2</md:revised>\n  <md:actors>\n    <md:person userid="rijk">\n      <md:firstname>Rijk</md:firstname>\n      <md:surname>Stofberg</md:surname>\n      <md:fullname>Rijk Stofberg</md:fullname>\n      <md:email>rijk@upfrontsystems.co.za</md:email>\n    </md:person>\n  </md:actors>\n  <md:roles>\n    <md:role type="author">rijk</md:role>\n    <md:role type="maintainer">rijk</md:role>\n    <md:role type="licensor">rijk</md:role>\n  </md:roles>\n  <md:license url="http://creativecommons.org/licenses/by/3.0/"/>\n  <!-- For information on license requirements for use or modification, see license url in the\n       above <md:license> element.\n       For information on formatting required attribution, see the URL:\n         CONTENT_URL/content_info#cnx_cite_header\n       where CONTENT_URL is the value provided above in the <md:content-url> element.\n  -->\n  <md:keywordlist>\n    <md:keyword>Arty stuff</md:keyword>\n  </md:keywordlist>\n  <md:subjectlist>\n    <md:subject>Arts</md:subject>\n  </md:subjectlist>\n  <md:abstract>Arty stuff module</md:abstract>\n  <md:language>en</md:language>\n  <!-- WARNING! The \'metadata\' section is read only. Do not edit above.\n       Changes to the metadata section in the source will not be saved. -->\n</metadata>\n\n<content>\n  <para id="delete_me">\n     <!-- Insert module text here -->\n  </para>\n</content>\n\n</document>\n'


one_link_reference_text = \
u'<?xml version="1.0"?>\n<document xmlns="http://cnx.rice.edu/cnxml" xmlns:md="http://cnx.rice.edu/mdml" xmlns:bib="http://bibtexml.sf.net/" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:q="http://cnx.rice.edu/qml/1.0" id="new" cnxml-version="0.7" module-id="new">\n\n<title>tm</title>\n<metadata mdml-version="0.5">\n  <!-- WARNING! The \'metadata\' section is read only. Do not edit below.\n       Changes to the metadata section in the source will not be saved. -->\n  <md:repository>http://localhost:8080/site/content</md:repository>\n  <md:content-id>new</md:content-id>\n  <md:title>tm</md:title>\n  <md:version>**new**</md:version>\n  <md:created>2011/10/11 15:13:54.863 GMT+2</md:created>\n  <md:revised>2011/10/11 15:13:54.975 GMT+2</md:revised>\n  <md:actors>\n    <md:person userid="rijk">\n      <md:firstname>Rijk</md:firstname>\n      <md:surname>Stofberg</md:surname>\n      <md:fullname>Rijk Stofberg</md:fullname>\n      <md:email>rijk@upfrontsystems.co.za</md:email>\n    </md:person>\n  </md:actors>\n  <md:roles>\n    <md:role type="author">rijk</md:role>\n    <md:role type="maintainer">rijk</md:role>\n    <md:role type="licensor">rijk</md:role>\n  </md:roles>\n  <md:license url="http://creativecommons.org/licenses/by/3.0/"/>\n  <!-- For information on license requirements for use or modification, see license url in the\n       above <md:license> element.\n       For information on formatting required attribution, see the URL:\n         CONTENT_URL/content_info#cnx_cite_header\n       where CONTENT_URL is the value provided above in the <md:content-url> element.\n  -->\n  <md:abstract/>\n  <md:language>en</md:language>\n  <!-- WARNING! The \'metadata\' section is read only. Do not edit above.\n       Changes to the metadata section in the source will not be saved. -->\n</metadata>\n<featured-links>\n  <!-- WARNING! The \'featured-links\' section is read only. Do not edit below.\n       Changes to the links section in the source will not be saved. -->\n    <link-group type="example">\n      <link url="http://localhost:8080/featured_module" strength="3">Test feature link</link>\n    </link-group>\n  <!-- WARNING! The \'featured-links\' section is read only. Do not edit above.\n       Changes to the links section in the source will not be saved. -->\n</featured-links>\n<content>\n  <para id="delete_me">\n     <!-- Insert module text here -->\n  </para>\n</content>\n\n</document>\n'


no_link_reference_meta = \
    {'mimetype': 'application/cmf+folderish',
     'featured_links': [],
     'properties': {},
     'encoding': None}

one_link_reference_meta = \
     {'mimetype': 'application/cmf+folderish',
      'featured_links': [{'url': 'http://localhost:8080/featured_module',
                          'strength': '3',
                          'type': 'example',
                          'title': 'Test feature link'}
                        ],
      'properties': {},
      'encoding': None
     }
