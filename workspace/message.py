import os
from colorama import Fore, Back, Style

def error(message):
  print(Style.BRIGHT + Fore.RED + message + Style.RESET_ALL)

def bright(message):
  print('')
  print(Style.BRIGHT + message + Style.RESET_ALL)

def run_or_fail(cmd):
  if os.system(cmd) != 0:
    error('Error while running '+cmd)
    exit()
