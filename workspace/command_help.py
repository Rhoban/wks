from colorama import Fore, Back, Style
from workspace import commands

name = "help"
help = """Provides help about commands"""
usage = ""
min_args = 0

def run(args):
  print('Available commands:')
  print('')

  for entry in commands.commands:
    print(Style.BRIGHT + Fore.BLUE + "./workspace" + Fore.RESET + " " + entry.name + ' ' + Style.RESET_ALL + entry.usage)
    lines = entry.help.strip().split("\n")
    lines = ["    " + line for line in lines]
    print("\n".join(lines))
    print('')