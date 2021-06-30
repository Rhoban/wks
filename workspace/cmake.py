from typing import Dict
from workspace import env, message, git
import os
from colorama import Fore, Back, Style
from leafy.digraph import DFS
from leafy.graph import Graph

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
  source_directories = git.get_directories(code_only=True)

  # construct dependency_graph
  dependency_graph = Graph(len(source_directories), True)
  directory_index = {}
  for index, directory in enumerate(source_directories):
    directory_index[directory] = index

  for directory in source_directories:
    config = env.get_config(directory)

    if config and 'deps' in config:
      for d in config['deps']:
        deps_dir = env.sources_directory + '/' + git.parse_repository_name(d)['full_name']
        dependency_graph.add_edge(directory_index[directory], directory_index[deps_dir])

  # add source directories
  already_add = [False] * len(source_directories) # support multiple dependency graph
  for source in dependency_graph.sources: 
    dfs = DFS(dependency_graph, source)
    dfs.run()

    if not dfs.is_dag:
      print(message.warn(f"Your dependency graph for {source_directories[source]} is not directed or acyclic !\n"))

    for node in list(dfs.reverse_topological_order()):
      if already_add[node]:
        continue
      directory = source_directories[node]
      cmakes = ['']

      config = env.get_config(directory)
      if config and 'cmakes' in config:
          cmakes = config['cmakes']
   
      cmake_directory = os.path.realpath(directory)
      dname = os.path.basename(os.path.dirname(directory))
      name = os.path.basename(directory)

      for cmake_name in cmakes:
        project = '%s/%s' % (dname, name)
        if cmake_name:
          project += '/' + cmake_name

        cmake += "add_subdirectory(%s)\n" % (project)
        already_add[node] = True
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

