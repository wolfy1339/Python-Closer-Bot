import sys


def confirm(self, question, answer="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "answer" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {
        "yes": True,
        "y": True,
        "ye": True,
        "no": False,
        "n": False
    }
    if answer is None:
        prompt = " [y/n] "
    elif answer == "yes":
        prompt = " [Y/n] "
    elif answer == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '{0}'".format(answer))

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if answer is not None and choice == '':
            return valid[answer]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")