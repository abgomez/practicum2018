# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import toml
import getpass
import logging
import argparse
import traceback
import pkg_resources

from colorlog import ColoredFormatter
from code_smell_client import codeSmellClient
from code_smell_exceptions import codeSmellException

DISTRIBUTION_NAME = 'sawtooth-code_smell'
HOME = os.getenv('SAWTOOTH_HOME')
DEFAULT_URL = 'http://127.0.0.1:8008'

def create_console_handler(verbose_level):
    """
    Create console handler, defines logging level

    Args:
        verbose_level (int): argument passed by user defining if verbose will be active

    Returns:
        clog: console handler to display verbose output
    """

    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG'    : 'cyan',
            'INFO'     : 'green',
            'WARNING'  : 'yellow',
            'ERROR'    : 'red',
            'CRITICAL' : 'red',
        })
    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def setup_loggers(verbose_level):
    """
    Set up level of verbose.

    Args:
        verbose_level (int): argument passed by user defining if verbose will be active
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_create_parser(subparser, parent_parser):
    """
    add_create_parser, add subparser create. this subparser will process new code smells.

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'create',
        help='Create new codeSmell <name>, <metric>',
        description='Send a transaction to create a new code smell',
        parents=[parent_parser])

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='unique code smell identifier')

    parser.add_argument(
        '-m', '--metric',
        type=str,
        help='metric of code smell')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    ## TODO: define if need it
    """parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API is using Basic Auth')"""

    parser.add_argument(
        '--disable-client-valiation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        default=10, ## TODO: update this value to something appropiate
        help='set time, in seconds, to wait for code smell to commit')

def add_default_parser(subparser, parent_parser):
    """
    add_default_parser, add subparser default. this subparser will load a
        default configuration for the code_smell family.

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'default',
        help='Load Default Configuration',
        description='Send transaction to load default configuration',
        parents=[parent_parser])

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    ## TODO: define if need it
    """parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API is using Basic Auth')"""

    parser.add_argument(
        '--disable-client-valiation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        default=10, ## TODO: update this value to something appropiate
        help='set time, in seconds, to wait for code smell to commit')

def create_parent_parser(prog_name):
    """
    Create parent parser

    Args:
        prog_name (str): program name

    Returns:
        parser: parent argument parser

    Raises:
        DistributionNotFound: version of family not found

    """
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}').format(version),
        help='display version information')

    return parent_parser

def create_parser(prog_name):
    """
    Function to create parent parser as well as subparsers.

    Args:
        prog_name (str): program name

    Returns:
        parser
    """
    parent_parser = create_parent_parser(prog_name)

    """create subparser, each subparser requires a different set of arguments."""
    parser = argparse.ArgumentParser(
        description='Suserum custom family (code_smell) to process and manage code smell transactions.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True
    add_create_parser(subparsers, parent_parser)
    add_default_parser(subparsers, parent_parser)

    return parser

def load_default(args):
    """
        load_default, function to load a set of default code smells.

        Args:
            args, arguments (array)
    """

    """identify code_smell family configuration file"""
    conf_file = HOME + '/etc/code_smell.toml'

    if os.path.isfile(conf_file):

        url = _get_url(args)
        keyfile = _get_keyfile(args)

        try:
            with open(conf_file) as config:
                raw_config = config.read()
        except IOError as e:
            raise codeSmellException ("Unable to load code smell family configuration file")

        """load toml config into a dict"""
        parsed_toml_config = toml.loads(raw_config)

        """get default code smells"""
        code_smells_config = parsed_toml_config['code_smells']

        """traverse dict and process each code smell
            nested for loop to procces level two dict."""
        for code_smells in code_smells_config.values():
            for name, metric in code_smells.items():
                """send trasaction"""
                client = codeSmellClient(base_url=url, keyfile=keyfile)
                if args.wait and args.wait > 0:
                    response = client.create(name, metric, "create", wait=args.wait)
                else:
                    response = client.create(name, metric, "create")
                print("Response: {}".format(response))
    else:
        raise codeSmellException("Configuration File {} does not exists".format(conf_file))

def do_create(args):
    """
    Create new code smell, users can define custom code smells.

    Args:
        args (array): code smell arguments

    Raises:
        codeSmellException: missing arguement
    """

    """validate arguments"""
    if args.name is not None:
        name = args.name
    else:
        raise codeSmellException ("Missing code smell name")

    if args.metric is not None:
        metric = args.metric
    else:
        raise codeSmellException ("Missing code smell metric")

    action = "create"

    url = _get_url(args)
    keyfile = _get_keyfile(args)

    print ("Payload: ", name, metric)

    ## TODO: define if we wantto create new codes smells for version one
    """client = codeSmellClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create(name, value, action, wait=args.wait)
    else:
        response = client.create(name, value, action)

    print("Response: {}".format(response))"""

def _get_url(args):
    """
    Pull rest_api url, use default if user does not specify

    Args:
        args (array): arguments from parser

    Returns:
        str: url of rest_api

    """
    return DEFAULT_URL if args.url is None else args.url

def _get_keyfile(args):
    """
    Retrives user's private key directory.
    Each transaction should be sign by the user who create it.

    Args:
        args (array): private key username

    Returns:
        str: path of user's private key
    """

    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)

## TODO: need to define if we are going to use user and password.
"""def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password
"""

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    """
    Expose core functionality of the code_smell family.

    Args:
        prog_name, program name (str)
        args, arguments to process code smells (array)
    """
    if args is None:
        args=sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'create':
        do_create(args)
    elif args.command == 'default':
        load_default(args)
    else:
        raise codeSmellException("Invalid command: {}".format(args.command))

def main_wrapper():
    """
    Wrapper to main function.

    Args:
        None

    Exceptions:
        codeSmellException
        KeyboardInterrupt
        BaseException
    """
    try:
        main()
    except codeSmellException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
