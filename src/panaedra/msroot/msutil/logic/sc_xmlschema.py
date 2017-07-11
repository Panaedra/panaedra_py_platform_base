"""
XML/XSD validation logic that automatically switches to SAX when needed, and uses the DOM for small files.

Python part of sc_xmlschema.cls, OpenEdge ABL.

Standalone python test:
# On any AIX server:
. $SCRIPTS/PythonpathSet testT # codeQok#7305
# Use no files (should give error):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema; sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'','cXmlSchema':''}''')"
# Use example files (should validate the xml, works on all of our AIX servers):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema; sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'%s','cXmlSchema':'%s'}'''%(os.environ['_PATH_']+'/systeemtst/vanwan_misc/_PPL_UNDISCLOSED__xsdvalidatietest_b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED___CCMPNY__CCMPNY_610361634001.xml',os.environ['_PATH_']+'/repo/wrkdev/tw/src/ini/xsd/b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED_.xsd',))"
"""

import ast
import json

from lxml import etree

class sc_xmlschema(object):
  
  @classmethod
  def ValidateXmlByXsd(cls,cDataIP):
    '''Called from Bridge.
    
    :param cDataIP: An ast literal_eval string, dictionary. Keys: cXmlSchema, cXmlFile
    :type  cDataIP: str 
    
    :rtype:   str
    :returns: Feedback: formatted json with indent 0.
    :raises:  

    '''
    
    try:
      tParam = ast.literal_eval(cDataIP)
    except ValueError:
      raise ValueError('Malformed input %r' % cDataIP)
    
    cXmlSchema=tParam['cXmlSchema']
    cXmlFile=tParam['cXmlFile']
    
    tRet = {'cValidationError':''}
    
    try:
      schema_root=etree.parse(cXmlSchema)
      xmlschema = etree.XMLSchema(schema_root)
      xmlparser = etree.XMLParser(schema=xmlschema)
      if cls._validate(xmlparser, cXmlFile):
        print "%s validates" % cXmlFile
      else:
        print "%s doesn't validate" % cXmlFile
    except (etree.XMLSchemaError, etree.XMLSyntaxError, IOError,) as e:
      print type(e).__name__, cXmlSchema, e.message
    
    return json.dumps(tRet,indent=0)     

  @classmethod
  def _validate(cls,xmlparser, xmlfilename):
    try:
      etree.parse(xmlfilename, parser=xmlparser)
      return xmlparser.error_log.last_error is None
    except (etree.XMLSchemaError, etree.XMLSyntaxError, IOError) as e:
      print type(e).__name__, e.message
      return False

#EOF
