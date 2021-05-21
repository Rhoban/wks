import os
import workspace.env
import workspace.git
import workspace.message
import workspace.cmake

name = 'cmake'
help = """(Re-)Generates the meta cmake"""
usage = ""
min_args = 0

def run(args):
  cmake.generate()
  
  
