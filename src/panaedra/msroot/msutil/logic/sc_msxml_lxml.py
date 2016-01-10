'''
Custom helper methods for the lxml python package
'''

import os

from lxml import etree
from lxml.etree import Element

if os.name != 'posix':
  from panaedra.mxroot.mxeclipse.logic.sc_hook_mxeclipse_debug import sc_hook_mxeclipse_debug


class sc_msxml_lxml(object):
  
  oDefaultParser = None
    
  @classmethod
  def GetFormattedXml(cls, oEtreeIP, oRawTransformCallback=None, cDocTypeIP = ''):
    '''
    Call etree.tostring, standardized to avoid binary differences in generated/committed xml files
    '''
    cRet = etree.tostring(oEtreeIP, pretty_print=True, encoding='utf-8', with_tail=True, doctype=cDocTypeIP)
    
    if not oRawTransformCallback is None:
      cRet = oRawTransformCallback(cRet)
    
    return cRet

  @classmethod
  def XmlFromString(cls,cXmlIP):
    if cls.oDefaultParser is None:
      cls.oDefaultParser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
    oEtree = etree.fromstring(cXmlIP, cls.oDefaultParser)
    return oEtree

  @classmethod
  def ChildnodesToDict(cls, oEtreeIP, cXpathRootIP, cChildnodenameIP, cXpathChildKeyIP, tNsIP):
    '''
    Create a dictionary by iteration the children of a node, and creating a key by 'text' of the supplied xpath.
    The python built-in Ellipsis object is used as a key to store the root node.
    '''
    tRet = {}
    
    oRoot = None
    for oXpath in oEtreeIP.xpath(cXpathRootIP, namespaces=tNsIP):
      oRoot = oXpath 
      break
    
    if oRoot is None:
      oRootParPar = None 
      if cXpathRootIP.endswith('/n:children/n:topics'):
        cXpathRootTrimmed = cXpathRootIP[0:cXpathRootIP.rindex('/n:children/n:topics')]
        for oXpath in oEtreeIP.xpath(cXpathRootTrimmed, namespaces=tNsIP):
          oRootParPar = oXpath 
          break
      if not oRootParPar is None:
        # Insert an empty children/topics tree
        oRootParPar.append(sc_msxml_lxml.XmlFromString(r'<children xmlns="urn:_3DP_:xmap:xmlns:content:2.0"><topics type="attached"/></children>'))
      # retry original xpath search
      for oXpath in oEtreeIP.xpath(cXpathRootIP, namespaces=tNsIP):
        oRoot = oXpath 
        break
      
    if oRoot is None and os.name != 'posix':
      sc_hook_mxeclipse_debug.MsgPopup('Error: Cannot find root with "%s"' % cXpathRootIP)

    cChildnodenameIP = sc_msxml_lxml.FullNamespaceByTree(oEtreeIP,cChildnodenameIP)
    
    if not oRoot is None:
      tRet[Ellipsis] = oRoot
      for oChild in oRoot.iterchildren(cChildnodenameIP):
        cKey = None
        for oXpath in oChild.xpath(cXpathChildKeyIP, namespaces=tNsIP):
          cKey = oXpath.text 
          break
        if not cKey is None:
          tRet[cKey] = oChild
          
    return tRet

  @classmethod
  def CompactNamespace(cls, oEtreeIP):
    tag = oEtreeIP.tag
    for ns in oEtreeIP.nsmap:
      prefix = '{' + oEtreeIP.nsmap[ns] + '}'
      if tag.startswith(prefix):               
        return ns + ':' + tag[len(prefix):]
    return tag

  @classmethod
  def FullNamespaceByTree(cls, oEtreeIP, cTagIOP):
    # Note: only no-namespace for now, adjust code when needed
    if cTagIOP.find(':') == -1 and cTagIOP.find('{') == -1 :
      if oEtreeIP.nsmap.has_key(None):
        cNs = oEtreeIP.nsmap[None]
        if len(cNs) > 0:
          cTagIOP = '{%s}%s' % (cNs,cTagIOP)
    return cTagIOP
  
  @classmethod
  def FullNamespaceByDict(cls, tDictIP, cTagIOP):
    # Note: only no-namespace for now, adjust code when needed
    if cTagIOP.find(':') == -1 and cTagIOP.find('{') == -1 :
      if tDictIP.has_key(None):
        cNs = tDictIP[None]
        if len(cNs) > 0:
          cTagIOP = '{%s}%s' % (cNs,cTagIOP)
    return cTagIOP
  
  @classmethod
  def WriteXmlToFile(cls, oTreeIP, cOutputFilepathIP, cDocTypeIP=''): 

    cFormattedXml = cls.GetFormattedXml(oTreeIP, cDocTypeIP=cDocTypeIP) 
    oFile = open(cOutputFilepathIP, 'w')
    oFile.write(cFormattedXml)
    oFile.close()
  
  @classmethod 
  def AppendNewElementToNode(cls, oNodeIP = '', cElementNameIP = '', cElementTextIP = '', tElementAttributeIP = {}):  
      
    oElement = Element(cElementNameIP) 
    # Add attributes to the element by a dictionary
    for cKey in tElementAttributeIP.keys(): 
      oElement.set(cKey, tElementAttributeIP[cKey])

    if cElementTextIP: 
      oElement.text = cElementTextIP

    oNodeIP.append(oElement)
      
    return oElement 
  
  @classmethod
  def GetParsedXmlFromFile(cls, cFilepathClasspath): 
    
    parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
    return etree.parse(cFilepathClasspath, parser)
  
#EOF
