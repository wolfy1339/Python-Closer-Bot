import sys
sys.path.insert(0, os.path.join(os.path.dirname(sys.modules[__name__].__file__), ".."))
from main import TPT

def main(arg):
    TPT().cleanThreads(confirm=not "--automatic" in arg, delete=not "--lock" in arg)
if __name__ == '__main__':
    # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).
    main(sys.argv[1:])
