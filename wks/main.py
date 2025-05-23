#!/usr/bin/env python

import sys
from . import message, commands, command_help

def main():    
    if len(sys.argv) <= 1:
        command_help.run(sys.argv[2:])
    else:
        for command in commands.commands:
            if command.name == sys.argv[1]:
                if len(sys.argv[2:]) < command.min_args:
                    message.error("Not enough arguments for command " + sys.argv[1])
                    if command.usage:
                        print("Usage: wks " + sys.argv[1] + " " + command.usage)
                else:
                    command.run(sys.argv[2:])
                exit()

        print(message.error("Error: command " + sys.argv[1] + " not found"))
        command_help.run([])

if __name__ == "__main__":
    main()