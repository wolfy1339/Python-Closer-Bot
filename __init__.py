def main(arg):
    if '--clean' in arg:
        if '--automatic' in arg:
            TPT().cleanThreads()
        else:
            TPT().cleanThreads(confirm=True)
    elif '--lock' in arg:
        if '--automatic' in arg:
            TPT().cleanThreads(delete=False)
        else:
            TPT().cleanThreads(confirm=True, delete=False)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])  # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).
