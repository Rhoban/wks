from colorama import Fore, Back, Style
from workspace import commands, message
import pkg_resources  # part of setuptools

name = "help"
help = """Provides help about commands"""
usage = ""
min_args = 0

def run(args):
    print('wks version %s' % pkg_resources.require("wks")[0].version)
    print('Available commands:')
    print('')

    for entry in commands.commands:
        message.bright(message.emphasis("wks") + " " + entry.name + ' ' + Style.RESET_ALL + entry.usage)
        lines = entry.help.strip().split("\n")
        lines = ["    " + line for line in lines]
        print("\n".join(lines))

    print('')