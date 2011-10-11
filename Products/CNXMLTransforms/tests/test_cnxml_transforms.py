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
        path = os.path.join(DIRNAME, 'data', 'no_links_reference.xml')
        file = open(path, 'rb')
        no_links_reference_text = file.read()
        file.close()

        self.assertEqual(
            returned_text,
            no_links_reference_text,
            'The text was not extracted correctly. (%s)' % \
                diff(returned_text, no_links_reference_text)
        )

        self.assertEqual(subobjs, {}, 'There should be no sub objects.')
        self.assertEqual(
            meta, 
            {'mimetype': 'application/cmf+folderish',
             'featured_links': [],
             'properties': {},
             'encoding': None},
            'Metadata was not set correctly.')

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

        path = os.path.join(DIRNAME, 'data', 'one_link_reference.xml')
        file = open(path, 'rb')
        one_link_reference_text = file.read()
        file.close()

        returned_text = text.read()
        self.assertEqual(
            returned_text,
            one_link_reference_text,
            'The text was not extracted correctly. (%s)' % \
                diff(returned_text, one_link_reference_text)
        )
        self.assertEqual(subobjs, {}, 'There should be no sub objects.')
        self.assertEqual(
            meta,
            {'mimetype': 'application/cmf+folderish',
             'featured_links': [{'url': 'http://localhost:8080/featured_module',
                                 'strength': '3',
                                 'type': 'example',
                                 'title': 'Test feature link'}
                               ],
             'properties': {},
             'encoding': None
            },
            'Metadata was not set correctly.')

    def test_import_existing_links(self):
        self.fail()

    def test_import_new_and_existing_links(self):
        self.fail()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCNXMLTransforms))
    return suite
