import argparse



class ArgsTypes:
    run: bool
    gui: bool
    log: bool
    file: str | None



parser = argparse.ArgumentParser(prog="Jabuti", description="Jabuti CLI")
parser.add_argument("-r", "--run", action="store_true", default=False,
    help="execute the file"
)
parser.add_argument("-g", "--gui", action="store_true", default=False,
    help="open the graphical interface"
)
parser.add_argument("-l", "--log", action="store_true", default=False,
    help="log the execution steps"
)
parser.add_argument("-f", "--file", help="relative file path, json or toml")

args: ArgsTypes = parser.parse_args()

# Nothing to do
if not args.run and not args.gui:
    print(f"\033[31mNo action to take\033[39m\n") # red
    parser.print_help()
    exit()

# Command to run has no file specified
if args.run and args.file is None:
    print(f"\033[31mNo file was specified to run\033[39m\n")
    parser.print_help()
    exit()

import jabuti as jb

# Runs the file on the background
if args.run and args.file is not None:
    print(f"\033[32mExecuting the file '{args.file}'\033[39m")
    exit()

# Opens the GUI
if args.gui:
    # With the specified file
    if args.file is not None:
        print(f"\033[32mOpening the file '{args.file}' on the GUI\033[39m")
    
    # With a new blank file
    else:
        print(f"\033[33mOpening a new GUI window\033[39m")
    
    exit()
