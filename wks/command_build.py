import subprocess
import os
from . import env, git, message, cmake

name = "build"
help = """Runs the build"""
usage = ""
min_args = 0


def run(args):
    result = 1
    message.bright("* Building")

    if not os.path.exists("build"):
        os.makedirs("build")

    run_cmake = not os.path.exists("build/CMakeCache.txt")

    cmd = "cd build;"
    if subprocess.getoutput("which ninja") != "":
        if run_cmake:
            cmd += "cmake -G Ninja ..;"
        cmd += "ninja %s" % " ".join(args)
        result = os.system(cmd)
    else:
        print(
            message.warn(
                "Ninja was not found, you can consider: apt-get install ninja-build"
            )
        )
        if input("Continue with Makefiles? (y/n) ") == "y":
            if run_cmake:
                cmd += "cmake ..;"
            cmd += "make %s" % " ".join(args)
            result = os.system(cmd)

    if result != 0:
        message.bright(
            message.error("\n! Errors while building, read log for more details\n")
        )
        exit(1)
    else:
        message.bright(message.success("\nBuild was successful\n"))
