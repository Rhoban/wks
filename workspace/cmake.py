from typing import Dict
from workspace import env, message, git
import os
from colorama import Fore, Back, Style

def generate():
  message.bright('* Generating CMake')
  print('')

  cmake = "cmake_minimum_required(VERSION 3.16.3)\n\n"

  for directory in git.get_directories():
    cmakes = ['']

    config = env.get_config(directory)
    if config and 'cmakes' in config:
      cmakes = config['cmakes']

    for cmake_name in cmakes:
      cmake_directory = os.path.realpath(directory)
      dname = os.path.basename(os.path.dirname(directory))
      name = os.path.basename(directory)
      project = '%s_%s' % (name, dname)

      if cmake_name:
        project += '_' + cmake_name
        cmake_directory += '/' + cmake_name

      cmake += "add_subdirectory(%s %s)\n" % (cmake_directory, project)
      print('- %s [%s]' % (project, Style.DIM + cmake_directory + Style.RESET_ALL))

  f = open(env.sources_directory + '/CMakeLists.txt', 'w')
  f.write(cmake)
  f.close()
  message.bright("* Wrote CMakeLists.txt")
  print('')
