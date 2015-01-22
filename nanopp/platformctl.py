import argparse
from nanopp import metadata

__author__ = 'pavle'


PROG_NAME='platfromctl'
DESCRIPTION='''
Run Nano Plugin Platform
'''

def create_arg_parser(prog_name):
    arg_parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(prog_name, metadata.version))

    arg_parser.add_argument(
        '-c', '--config-file',
        default='platform.ini',
        help='Platform configuration file.'
    )

    arg_parser.add_argument(
        '-d', '--plugins-directory',
        default='plugins',
        help='Plugins directory'
    )

    return arg_parser

def create_platform_instance(args):
    pass

def ctl_main():
    parser = create_arg_parser(PROG_NAME)
    args = parser.parse_args()
