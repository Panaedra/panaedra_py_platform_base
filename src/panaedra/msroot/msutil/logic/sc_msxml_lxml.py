"""
Custom helper methods for the lxml python package
"""

from lxml import etree

class sc_msxml_lxml(object):
  
  @staticmethod
  def GetFormattedXml(oEtreeIP):
    """Call etree.tostring, standardized to avoid binary differences in generated/committed xml files"""
    cRet = etree.tostring(oEtreeIP, pretty_print=True, encoding="utf-8", with_tail=True)
    return cRet
    
#EOF
