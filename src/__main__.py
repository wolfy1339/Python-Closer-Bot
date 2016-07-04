from main import TPT

import os
import sys
path = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, os.path.join(path, ".."))

x = TPT()


def main(arg):
    """Wrapper function to pass arguments to the cleanThreads function"""
    confirm = "--automatic" not in arg
    delete = "--lock" not in arg
    x.cleanThreads(confirm=confirm, delete=delete)

if __name__ == '__main__':
    # Execute 'main' with all the command line arguments.
    main(sys.argv[1:])
