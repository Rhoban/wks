import os
import subprocess
from colorama import Fore, Back, Style
from workspace import env, git, message, cmake

name = "install-requirements"
help = """Install packages requirements"""
usage = ""
min_args = 0


def run(args):
    for directory in git.get_directories():
        config = env.get_config(directory)

        if config is not None and "requirements" in config:
            message.bright(f"* Executing requirements for {directory}")
            for entry in config["requirements"]:
                os.system(f"cd {directory}; {entry}")