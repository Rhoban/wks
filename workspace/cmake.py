from typing import Dict
from workspace import env, message, git
import os
from colorama import Fore, Back, Style

toplevel_cmake = """
cmake_minimum_required(VERSION 3.16.3)
project(wks)

# Libs are in lib/ and binaries in bin/
include(GNUInstallDirs)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})

add_subdirectory(src)
"""

cmake_headers = """
cmake_minimum_required(VERSION 3.16.3)

# Colored compiler output
add_compile_options(
  $<$<CXX_COMPILER_ID:GNU>:-fdiagnostics-color=always>
  $<$<CXX_COMPILER_ID:Clang>:-fcolor-diagnostics>
)

# Easy build type selection
set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS Release Debug RelWithDebInfo)

# Generate compile_commands.json to make it easier to work with clang based tools
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Create profile for profiling with gprof
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  set(CMAKE_C_FLAGS_PROFILE
    "${CMAKE_C_FLAGS_RELWITHDEBINFO} -p" CACHE STRING "")
  set(CMAKE_CXX_FLAGS_PROFILE
    "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} -p" CACHE STRING "")
  set(CMAKE_EXE_LINKER_FLAGS_PROFILE
    "${CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO} -p" CACHE STRING "")
  set(CMAKE_SHARED_LINKER_FLAGS_PROFILE
    "${CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO} -p" CACHE STRING "")
  set(CMAKE_STATIC_LINKER_FLAGS_PROFILE
    "${CMAKE_STATIC_LINKER_FLAGS_RELWITHDEBINFO}" CACHE STRING "")
  set(CMAKE_MODULE_LINKER_FLAGS_PROFILE
    "${CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO} -p" CACHE STRING "")
  mark_as_advanced(FORCE CMAKE_C_FLAGS_PROFILE CMAKE_CXX_FLAGS_PROFILE CMAKE_EXE_LINKER_FLAGS_PROFILE CMAKE_SHARED_LINKER_FLAGS_PROFILE CMAKE_STATIC_LINKER_FLAGS_PROFILE CMAKE_MODULE_LINKER_FLAGS_PROFILE)
  ## set postfix for binaries
  set(CMAKE_PROFILE_POSTFIX _profile)

  ## Add Profile to selectable build types
  set_property(CACHE CMAKE_BUILD_TYPE APPEND PROPERTY STRINGS Profile)
endif()


"""

def generate():
  message.bright('* Generating CMake')
  print('')

  cmake = cmake_headers

  for directory in git.get_directories():
    cmakes = ['']

    config = env.get_config(directory)
    if config and 'cmakes' in config:
      cmakes = config['cmakes']

    for cmake_name in cmakes:
      cmake_directory = os.path.realpath(directory)
      dname = os.path.basename(os.path.dirname(directory))
      name = os.path.basename(directory)
      project = '%s_%s' % (dname, name)

      if cmake_name:
        project += '_' + cmake_name
        cmake_directory += '/' + cmake_name

      cmake += "add_subdirectory(%s %s)\n" % (cmake_directory, project)
      print('- %s [%s]' % (project, Style.DIM + cmake_directory + Style.RESET_ALL))

  f = open(env.sources_directory + '/CMakeLists.txt', 'w')
  f.write(cmake)
  f.close()

  if not os.path.exists('CMakeLists.txt'):
      message.bright("* No top-level CMakeLists.txt found, generating one...")
      f = open('CMakeLists.txt', 'w')
      f.write(toplevel_cmake)
      f.close()

  message.bright("* Wrote CMakeLists.txt")
  print('')
