"""
Transform  Rhaptos module into offline viewable XHTML.

The main part of the returned idata (getData) will be Zip file
containing the XHTML, other module components, and styles for offline
viewing. There will be no sub objects (getSubObjects).

Set parameter to choose an alternate stylesheet supplier.
"""
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import itransform

from Products.RhaptosContent import MODULE_XSL

from ZipExport import makeZipFile

# yes, this is cheap, but it's short, so I can get away with it
offlinecss = """#nostyles { display:none; }"""
README = """This is an export of a module with a special XHTML file and stylesheets included so that it can be viewed offline.

Any changes to the XHTML file (index.xhtml) or the stylesheets will be lost if this zip file is imported. Any other subdirectories will also be ignored.

Also, please note that, at least under Windows, if you open the index.xhtml file directly from the zip file, it will display in black and white because it can't see the stylesheets. Extract the whole thing and it'll work right.
"""

def getStyles():
    """Supply a list of styles available in the offline package.
    Returns a list of dictionaries much like 'getStyles' in the skins but with an additional key:
    
      'source': a path under the skins tool (including layer name) to include in the zip file.
      This folder and its contents will be placed under 'stylesheets/' in the zip file.
      Only static contents (FSImages and FSFiles, Images and Files) supported, due to off-line use.
    """
    return [{'id':'sky','title':"Summer Sky",'path':'stylesheets/sky/document.css','active':1,
             'source':'CNXContent/cnx-styles/sky'}]

class module_to_xhtmlzip:
    """Transform CNXML into Authentic CNXML."""
    __implements__ = itransform
    
    __name__ = "module_to_xhtmlzip"
    inputs  = ("application/cmf+folderish",)
    output = "application/zip"
    
    config = {
        'stylesheet_method':'',
    }
    config_metadata = {
        'stylesheet_method':('string', 'Alternate style sheet method',
                             'To supply a different set of styles, provide a name to an acquirable method to supplant XHTMLExport.getStyles',),
    }
    
    def name(self):
        return self.__name__

    def convert(self, data, outdata, **kwargs):
        """Input is a module object. Output is idata, but getData returns a binary zip file."""
        #text = data.module_render()
        
        kw = {}
        #kw.update(data.getCourseParameters())
        styleMethod = self.config['stylesheet_method']
        if styleMethod: styleMethod = getattr(data, styleMethod, None)
        if styleMethod: styles = styleMethod()
        else: styles = getStyles()
        kw["styles"] = styles
        if len(styles) <= 1: kw["style_chooser"] = 0
        
        kw['offline'] = 1
        
        source = data.module_export_template(**kw)
        text = data.cnxml_transform(source, stylesheet=MODULE_XSL)
        
        container = data.getId().replace('.','-')
        content, zipfile = makeZipFile(data, container)
        zipfile.writestr('%s/index.xhtml' % container, text)
        zipfile.writestr("%s/README.txt" % container, README)
        
        zipfile.writestr("%s/stylesheets/offline.css" % container, offlinecss)
        for style in styles:
            styleloc = style['source']
            wf = getToolByName(data, 'portal_skins')
            folder = wf.restrictedTraverse(styleloc)
            stylepath = "%s/stylesheets/%s" % (container, folder.getId())
            for ob_id, ob in folder.objectItems():
                val = getattr(ob, '_readFile', None)
                if val: val = val(0)                             # get value from FSImage or FSFile
                else:   val = str(getattr(ob, 'data', ob))       # get value from Image or File, with vaguely reasonable default
                zipfile.writestr('/'.join((stylepath, ob_id)), val)
        
        zipfile.close()
        outdata.setData(content.getvalue())
        content.close()
        # nothing to do for outdata.setSubObjects(objects)
        return outdata

def register():
    return module_to_xhtmlzip()