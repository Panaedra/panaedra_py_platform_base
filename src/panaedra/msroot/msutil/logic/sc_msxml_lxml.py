"""
Custom helper methods for the lxml python package
"""

from lxml import etree

class sc_msxml_lxml(object):
  
  @staticmethod
  def GetFormattedXml(oEtreeIP):
    """
    Call etree.tostring, standardized to avoid binary differences in generated/committed xml files
    """
    cRet = etree.tostring(oEtreeIP, pretty_print=True, encoding="utf-8", with_tail=True)
    return cRet
    
  @staticmethod
  def ChildnodesToDict(oEtreeIP, cXpathRootIP, cChildnodenameIP, cXpathChildKeyIP, tNsIP):
    """
    Create a dictionary by iteration the children of a node, and creating a key by 'text' of the supplied xpath.
    The python built-in Ellipsis object is used as a key to store the root node.
    """
    tRet = {}
    
    oRoot = None
    for oXpath in oEtreeIP.xpath(cXpathRootIP, namespaces=tNsIP):
      oRoot = oXpath 
      break
    
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

  @staticmethod
  def CompactNamespace(oEtreeIP):
    tag = oEtreeIP.tag
    for ns in oEtreeIP.nsmap:
      prefix = "{"+oEtreeIP.nsmap[ns]+"}"
      if tag.startswith(prefix):               
        return ns+":"+tag[len(prefix):]
    return tag

  @staticmethod
  def FullNamespaceByTree(oEtreeIP, cTagIOP):
    # Note: only no-namespace for now, adjust code when needed
    if cTagIOP.find(':') == -1 and cTagIOP.find('{') == -1 :
      if oEtreeIP.nsmap.has_key(None):
        cNs = oEtreeIP.nsmap[None]
        if len(cNs) > 0:
          cTagIOP = '{%s}%s' % (cNs,cTagIOP)
    return cTagIOP
  
  @staticmethod
  def FullNamespaceByDict(tDictIP, cTagIOP):
    # Note: only no-namespace for now, adjust code when needed
    if cTagIOP.find(':') == -1 and cTagIOP.find('{') == -1 :
      if tDictIP.has_key(None):
        cNs = tDictIP[None]
        if len(cNs) > 0:
          cTagIOP = '{%s}%s' % (cNs,cTagIOP)
    return cTagIOP
  
#EOF
