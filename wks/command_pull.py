import os
from . import env, git, message, cmake

name = "pull"
help = """Pull all the repositories"""
usage = ""
min_args = 0


def run(args):
    vendor_filter = None if (len(args) == 0) else args[0]
    git.global_command("git pull", vendor_filter)
    git.scan_all_dependencies()
    cmake.generate()
