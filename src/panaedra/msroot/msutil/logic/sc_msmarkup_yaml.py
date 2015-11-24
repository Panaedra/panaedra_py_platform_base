import yaml

from collections import OrderedDict

class sc_msmarkup_yaml(object):
  
  @classmethod
  def ordered_load(cls, stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    '''Like YAML load, but load into an OrderedDict'''
    class OrderedLoader(Loader):
      pass
    def construct_mapping(loader, node):
      loader.flatten_mapping(node)
      return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
      yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
      construct_mapping)
    return yaml.load(stream, OrderedLoader)
  
  
  @classmethod
  def ordered_dump(cls, data, stream=None, Dumper=yaml.Dumper, **kwds):
    '''Like YAML dump, but dump from an OrderedDict'''
    class OrderedDumper(Dumper):
      pass
    def _dict_representer(dumper, data):
      return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)
  
#EOF
