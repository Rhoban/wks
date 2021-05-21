import os
from workspace import env, git, message, cmake

name = 'pull'
help = """Pull all the repositories"""
usage = ""
min_args = 0

def run(args):
  git.global_command('git pull')
  