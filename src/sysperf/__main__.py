import argparse
import sysperf
from sysperf import __version__


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser('sysperf')
    version = '%(prog)s ' + __version__
    parser.add_argument('--version', '-v', action='version', version=version)
    return parser

def main(args=None):
    """
    Main entry point for your project.

    Args:
        args : list
            A of arguments as if they were input in the command line. Leave it
            None to use sys.argv.
    """

    parser = get_parser()
    args = parser.parse_args(args)

    # Put your main script logic here
    print('No action defined for sysperf module!')


if __name__ == '__main__':
    main()