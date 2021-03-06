"""
Transform a Sword Zip file to CNXML module.

The main part of the returned idata (getData) will be the
index.cnxml file. The sub objects (getSubObjects) will be
the other objects in the module, which should be siblings to
the CNXML file.

Parameter 'data' is expected to be a binary zipfile. The contents
will be a Word file and a mets.xml file

Not certified for nested contents.

NOTE: see OOoTransform header about compatibility with Archetypes fields.
"""
import demjson as json
from zipfile import ZipFile
from StringIO import StringIO
import os
import zLOG

from xml.dom.minidom import parseString

from Products.PortalTransforms.interfaces import itransform
from Products.CNXMLTransforms.OOoImport import oo_to_cnxml
from Products.CNXMLTransforms.LatexImport import latex_to_folder
from Products.CNXMLDocument import XMLService
from helpers import CNXImportError
from helpers import SWORD2RME_XSL
from helpers import SWORD_INSERT_ATTRIBUTION_XSL
from helpers import XML2JSON_XSL

class sword_to_folder:
    """Transform zip file to RhaptosModuleEditor with contents."""
    __implements__ = itransform

    __name__ = "sword_to_folder"
    inputs  = ("application/zip",)
    output = "application/cmf+folderish"
    encoding = 'utf-8'

    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        """Input is a zip file. Output is idata, with getData being index.cnxml and subObjects being other siblings."""
        fakefile = StringIO(data)
        zipfile = ZipFile(fakefile, 'r')

        prefix = ''
        namelist = zipfile.namelist()
        lenlist = len(namelist)
        if lenlist > 1:
            prefix = os.path.commonprefix(namelist)
            lastslash = prefix.rfind("/")
            if lastslash != -1: prefix = prefix[:lastslash+1]
            else: prefix = ''
        elif lenlist == 1:
            name = namelist[0]
            lastslash = name.rfind("/")
            if lastslash != -1: prefix = name[:lastslash+1]
        namelist = [name[len(prefix):] for name in namelist] # Strip prefix from namelist entries

        zLOG.LOG("Sword Transform", zLOG.INFO, "files in zip=%s" % namelist)
        meta = outdata.getMetadata()
        meta['properties'] = {}
        objects = {}

        containsIndexCnxml = ('index.cnxml' in namelist)
        wordfiles = len([True for m in namelist for e in \
                                ('.odt', '.sxw', '.docx', \
                                '.rtf', '.doc') if m.endswith(e)])
        latexfiles = len([True for m in namelist if m.endswith('.tex')])

        if sum([int(containsIndexCnxml), wordfiles, latexfiles]) > 1:
            # The upload contains more than one transformable file, ie
            # it has a index.cnxml and latex/word content, or it has both latex
            # and word content, or more than one latex or word file.
            raise CNXImportError(
                "Import has more than one transformable file. It has "
                "%d index.cnxml files, %d word files and "
                "%d LaTeX files" % (containsIndexCnxml, wordfiles, latexfiles))

        for modname in namelist:
            if not modname:               # some zip programs show directories by themselves
              continue
            isubdir = modname.find('/')
            if isubdir != -1:             # subdirs, incl. especially 'stylesheets', not imported
              continue
            unzipfile = zipfile.read(prefix + modname)
            if modname == "mets.xml":
                # Write metadata
                zLOG.LOG("Sword Transform", zLOG.INFO, "starting...")
                simplified = XMLService.transform(unzipfile, SWORD2RME_XSL)
                jsonstr = XMLService.transform(simplified, XML2JSON_XSL)
                m = json.decode(jsonstr)
                meta['properties'] = m
            elif modname == "index.cnxml":
                # hook here for featured links
                # elaborate the metadata returned in order to add the featured links.
                meta['featured_links'] = []
                if unzipfile:
                    outdata.setData(StringIO(unzipfile))
                    dom = parseString(unzipfile)
                    groups = dom.getElementsByTagName('link-group')
                    links = meta.get('featured_links', [])
                    for group in groups:
                        group_type = group.getAttribute('type').encode(self.encoding)
                        for link in group.getElementsByTagName('link'):
                            title = link.firstChild.toxml().encode(
                                self.encoding)
                            url = link.getAttribute('url').encode(
                                self.encoding)
                            strength = link.getAttribute('strength').encode(
                                self.encoding)
                            links.append({'url':url,
                                          'title':title,
                                          'type':group_type,
                                          'strength':strength
                                         }
                            )
                        meta['featured_links'] = links
            else:
                if not containsIndexCnxml:
                    if [True for e in ('.odt', '.sxw', '.docx', \
                        '.rtf', '.doc') if modname.endswith(e)]:
                        # This is a word file
                        oo_to_cnxml().convert(unzipfile, outdata, **kwargs)
                    elif modname.endswith('.tex'):
                        # This is LaTeX
                        latex_to_folder().convert(unzipfile, outdata,
                                        original_file_name='sword-import-file.tex',
                                        user_name=kwargs['user_name'])
                        # LaTeX transform returns straight text, make it
                        # a file object
                        outdata.setData(StringIO(outdata.getData()))
                    else:
                        objects[modname] = unzipfile
                else:
                    objects[modname] = unzipfile

        zipfile.close()
        fakefile.close()

        meta = outdata.getMetadata()

        # Add attribution note to the cnxml
        props = meta['properties']
        params = {}
        for key in ('journal', 'year', 'url'):
          if unicode(key) in props:
            value = props[unicode(key)]
            if isinstance(value, unicode):
              value = value.encode('utf-8')
            params[key] = value

        zLOG.LOG("Sword Transform", zLOG.INFO, "attribution dict=%s" % params)
        data = outdata.getData()

        if data and len(data.getvalue()) > 0:
          attributed = XMLService.transform(data.getvalue(), SWORD_INSERT_ATTRIBUTION_XSL, **params)
          outdata.setData(StringIO(unicode(attributed,'utf-8')))
        else:
          zLOG.LOG("Sword Transform", zLOG.INFO, "Skipping adding attributions because no cnxml was generated...")

        #meta['subdirs'] = subdirs.keys()

        objects.update(outdata.getSubObjects())
        outdata.setSubObjects(objects)

        return outdata


def register():
    return sword_to_folder()

