"""Command Line Interface for the bot"""
import os
import sys

from .main import TPT

path = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, os.path.join(path, ".."))

x = TPT()


def main(arg):
    """Wrapper function to pass arguments to the cleanThreads function"""
    doConfirm = "--automatic" not in arg
    delete = "--lock" not in arg
    x.cleanThreads(doConfirm=doConfirm, delete=delete)

if __name__ == '__main__':
    # Execute 'main' with all the command line arguments.
    main(sys.argv[1:])

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
