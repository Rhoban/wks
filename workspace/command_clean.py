import subprocess
import os
from workspace import env, git, message, cmake

name = "clean"
help = """Cleans the build"""
usage = ""
min_args = 0


def run(args):
    message.bright("* Cleaning")

    if subprocess.getoutput("which ninja") != "":
        cmd = "cd build; ninja clean"
        os.system(cmd)
    else:
        print(message.warn("Ninja was not found, you can consider: apt-get install ninja-build"))
        if input("Continue with Makefiles? (y/n) ") == "y":
            cmd = "cd build; make clean"
            os.system(cmd)

    message.bright(message.success("\nBuild was successful\n"))
