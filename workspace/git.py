import yaml
import subprocess
import os
from workspace import env, message, env

def parse_repository_name(name):
  parts = name.split('/')

  if len(parts) != 2:
    message.error('Bad repository name: ' + name)
    exit()

  repository = {
    'vendor': parts[0],
    'name': parts[1],
    'branch': None,
    'tag': None
  }

  markers = {'#': 'branch', '@': 'tag'}

  for marker in markers:
    if marker in repository['name']:
      name, value = repository['name'].split(marker, 1)
      repository['name'] = name
      repository[markers[marker]] = value

  repository['directory'] = env.sources_directory + '/' + repository['vendor'] + '/' + repository['name']
  repository['git'] = 'git@github.com:%s/%s.git' % (repository['vendor'], repository['name'])
  repository['full_name'] = '%s/%s' % (repository['vendor'], repository['name'])

  return repository

def install(repository_name):
  repository = parse_repository_name(repository_name)
  
  if not os.path.exists(repository['directory']):
    message.bright('* Installing ' + repository_name + '...')
    vendor_dir = os.path.dirname(repository['directory'])

    if not os.path.exists(vendor_dir):
      os.makedirs(vendor_dir)
    
    branch = ''
    if repository['branch']:
      branch = '--branch '+repository['branch']
    if repository['tag']:
      branch = '--branch '+repository['tag']

    cmd = 'git clone %s %s %s' % (branch, repository['git'], repository['directory'])

    message.run_or_fail(cmd)

    return True
  else:
    return False

def get_directories(directory=None):
  directories = []
  if directory is None:
    directory = env.sources_directory

  if not os.path.isdir(directory):
    message.die("Directory %s does not exists" % directory)
  
  for entry in os.scandir(directory):
    full_name = directory + '/' + entry.name
    if os.path.isdir(full_name):
      if os.path.isdir(full_name+'/.git'):
        directories.append(full_name)
      else:
        directories += get_directories(full_name)

  return directories

def scan_dependencies(directory):
  changed = False
  config = env.get_config(directory)
  
  if config and 'deps' in config:
    for entry in config['deps']:
      if install(entry):
        changed = True

  return changed

def scan_all_dependencies():
  message.bright('* Scanning all dependencies')
  changed = True

  while changed:
    changed = False
    for directory in get_directories():
      if scan_dependencies(directory):
        changed = True

def global_command(command):
  message.bright("* Running global command: %s" % command)

  for directory in get_directories():
    message.bright('- In %s ...' % os.path.realpath(directory))
    cmd = 'cd %s; %s' % (directory, command)
    os.system(cmd)
  
  print('')

def status(directory):
  output = subprocess.getoutput("cd %s; git status --porcelain=v1" % directory)
  return output

def branch(directory):
  output = subprocess.getoutput("cd %s; git branch" % directory)[2:]
  return output

def is_ahead(directory):
  ret, output = subprocess.getstatusoutput("cd %s; git rev-list @{u}.." % directory)
  return ret == 0 and output.strip() != ''