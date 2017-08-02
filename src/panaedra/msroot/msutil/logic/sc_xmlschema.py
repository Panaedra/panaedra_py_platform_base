"""
XML/XSD validation logic that automatically switches to SAX when needed, and uses the DOM for small files.

Python part of sc_xmlschema.cls, OpenEdge ABL.

Standalone python test:
# On any AIX server:
. $SCRIPTS/PythonpathSet testT # codeQok#7305
# Use no files (should give error):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema; sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'','cXsdFile':''}''')"
# Use example files (should validate the xml, works on all of our AIX servers):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema; sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'%s','cXsdFile':'%s'}'''%(os.environ['_PATH_']+'/systeemtst/vanwan_misc/_PPL_UNDISCLOSED__xsdvalidatietest_b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED___CCMPNY__CCMPNY_610361634001.xml',os.environ['_PATH_']+'/repo/wrkdev/tw/src/ini/xsd/b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED_.xsd',))"
"""

import ast
import ctypes
import json
import os

class sc_xmlschema(object):
  
  _bInitialized=False
  _Etree=None
  
  @classmethod
  def _Initialize(cls):
    if not cls._bInitialized:
      cls._bInitialized=True
      RTLD_MEMBER =  0x040000
      from _ctypes import RTLD_LOCAL, RTLD_GLOBAL  # @UnusedImport
      flags = RTLD_MEMBER
      flags |= RTLD_LOCAL
      testlib = ctypes.CDLL("libc.a(shr_64.o)", flags)
      testlib = ctypes.CDLL("/usr/lib/libcrypt.a(shr_64.o)", flags)
      testlib = ctypes.CDLL("/opt/freeware/lib/libiconv.a(libiconv.so.2)", flags)
#       raise Exception(repr(dir(testlib)))
      testlib = ctypes.CDLL("/opt/freeware/lib/libxml2.a(libxml2.so.2)", flags)
      testlib = ctypes.CDLL("/opt/freeware/lib/libxslt.a(libxslt.so.1)", flags)
#       raise Exception("test 2")
#       testlib = ctypes.CDLL("/opt/freeware/lib/libexslt.a(libexslt.so.0)", flags)
#       raise Exception("test 3")
#       testlib = ctypes.CDLL("/opt/freeware/lib/libxslt.a(libxslt.so.1)", flags)
#       raise Exception("test 4")
#       testlib = ctypes.CDLL('/opt/freeware/lib/libxslt.a(libxslt.so.1)')
      print testlib
      from lxml import etree
      cls._Etree=etree

  @classmethod
  def ValidateXmlByXsd(cls,cDataIP):
    '''Called from Bridge.
    
    :param cDataIP: An ast literal_eval string, dictionary. Keys: cXsdFile, cXmlFile
    :type  cDataIP: str 
    
    :rtype:   str
    :returns: Feedback: formatted json with indent 0.
    :raises:  

    '''
    
    try:
      cls._Initialize()
    except Exception as e:
      tRet = {'cValidationError': repr(('getcwd:',os.getcwd(),'exception:',e,))}
      return json.dumps(tRet,indent=0)
      
    try:
      tParam = ast.literal_eval(cDataIP)
    except ValueError:
      raise ValueError('Malformed input %r' % cDataIP)
    cXsdFile=tParam['cXsdFile']
    cXmlFile=tParam['cXmlFile']
    
    tRet = {'cValidationError':''}
    
    try:
      schema_root=cls._Etree.parse(cXsdFile)
      xmlschema = cls._Etree.XMLSchema(schema_root)
      xmlparser = cls._Etree.XMLParser(schema=xmlschema)
      if cls._validate(xmlparser, cXmlFile):
        print "%s validates" % cXmlFile
      else:
        print "%s doesn't validate" % cXmlFile
    except (cls._Etree.XMLSchemaError, cls._Etree.XMLSyntaxError, IOError,) as e:
      print type(e).__name__, cXsdFile, e.message
    
    return json.dumps(tRet,indent=0)     

  @classmethod
  def _validate(cls,xmlparser, xmlfilename):
    try:
      cls._Etree.parse(xmlfilename, parser=xmlparser)
      return xmlparser.error_log.last_error is None
    except (cls._Etree.XMLSchemaError, cls._Etree.XMLSyntaxError, IOError) as e:
      print type(e).__name__, e.message
      return False

#EOF
