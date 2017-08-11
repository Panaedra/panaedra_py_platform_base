"""
XML/XSD validation logic that automatically switches to SAX when needed, and uses the DOM for small files.

Python part of sc_xmlschema.cls, OpenEdge ABL.

Standalone python test:
# On any AIX server:
. $SCRIPTS/PythonpathSet testT # codeQok#7305
# Use no files (should give error):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema;x=sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'','cXsdFile':''}''');print x"
# Use example files (should validate the xml, works on all of our AIX servers):
clear && python -c "import os; from panaedra.msroot.msutil.logic.sc_xmlschema import sc_xmlschema;x=sc_xmlschema.ValidateXmlByXsd('''{'cXmlFile':'%s','cXsdFile':'%s'}'''%(os.environ['_PATH_']+'/systeemtst/vanwan_misc/_PPL_UNDISCLOSED__xsdvalidatietest_b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED___CCMPNY__CCMPNY_610361634001.xml',os.environ['_PATH_']+'/repo/wrkdev/tw/src/ini/xsd/b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED_.xsd',));print x"
"""

import ast
import json
import os
import traceback

class sc_xmlschema(object):
  
  _bInitialized=False
  _Etree=None
  
  @classmethod
  def _Initialize(cls):
    if not cls._bInitialized:
      cls._bInitialized=True
      # Note: We put this import in an initialization method, because:
      #       On AIX loading of lxml can be non-trivial. We had to customize builds
      #       of libxml2 and libxslt because of LIBPATH + embedding issues.
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
    tError=[]
    try:
      schema_root=cls._Etree.parse(cXsdFile)
      xmlschema = cls._Etree.XMLSchema(schema_root)
      xmlparser = cls._Etree.XMLParser(schema=xmlschema)
      if os.path.getsize(cXmlFile) < 10000000: # Size in bytes. Bigger than about 10MB is handled in a SAX manner.
        aValidate=cls._validate
      else:
        aValidate=cls._validate_big
      if not aValidate(xmlparser, cXmlFile, xmlschema):
        tError.append('''%s doesn't validate''' % cXmlFile)
    
    except (cls._Etree.XMLSchemaError, cls._Etree.XMLSyntaxError, IOError, OSError) as e:
      tError.append(traceback.format_exc())

    tRet['cValidationError']='\n'.join(tError)
    return json.dumps(tRet,indent=0)

  @classmethod
  def _validate(cls, xmlparser, xmlfilename, xmlschema):
    '''Simple DOM validation through etree.parse'''
    cls._Etree.parse(xmlfilename, parser=xmlparser)
    # Safety return, in case lxml does not throw on error
    return xmlparser.error_log.last_error is None

  @classmethod
  def _validate_big(cls, xmlparser, xmlfilename, xmlschema):
    '''Streaming SAX parsing, can be used for validating XML files of several gigabytes'''
    parse_context = cls._Etree.iterparse(xmlfilename, events=('end',), schema=xmlschema) # parser=xmlparser
    for _action, elem in parse_context:
      # cleanup
      # first empty children from current element
        # This is not absolutely necessary if you are also deleting siblings,
        # but it will allow you to free memory earlier.
      elem.clear()
      # second, delete previous siblings (records)
      while elem.getprevious() is not None:
        del elem.getparent()[0]
      # make sure you have no references to Element objects outside the loop
    # Safety return, in case lxml does not throw on error
    return xmlparser.error_log.last_error is None

'''
if __name__ == '__main__':
  os.environ['_PATH_']=r'Q:\ota'
  x=sc_xmlschema.ValidateXmlByXsd("""{'cXmlFile':'%s','cXsdFile':'%s'}"""%(os.environ['_PATH_']+'/systeemtst/vanwan_misc/_PPL_UNDISCLOSED__xsdvalidatietest_b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED___CCMPNY__CCMPNY_610361634001.xml',os.environ['_PATH_']+'/repo/wrkdev/tw/src/ini/xsd/b_TERM__TERM_UNDISCLOSED___TERM_UNDISCLOSED_.xsd',));print x
'''

#EOF
