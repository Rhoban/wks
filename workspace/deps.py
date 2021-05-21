import os
import yaml

def get_config(directory):
  deps_filename = directory + '/deps.yml'
  if os.path.exists(deps_filename):
    f = open(deps_filename, 'r')
    deps = yaml.load(f, Loader=yaml.Loader)

    return deps
    
  return None