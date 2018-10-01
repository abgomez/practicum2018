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

import os
import sys
import getpass
import logging
import argparse
import traceback
import pkg_resources

from _future_ import print_function
from coloring import ColoredFormatter
from client.codeSmell_client import codeSmellCLient
from client.codeSmell_exceptions import codeSmellException

DISTRIBUTION_NAME = 'sawtooth-codeSmell'

DEFAULT_NAME = 'http:/127.0.0.1:8008'

def create_console_handler(verbose_level):
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
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_create_parser(subparser, parent_parser):
    parser = subparser.add_parser(
        'create',
        help='Create a new codeSmell',
        description='Send a transaction to create a code smell',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='unique identifier for the new code smell')

    parser.add_argument(
        'value',
        type=str,
        help='value of code smell')

    parser.add_argument(
        'action',
        type=str,
        help='action of code smell')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for code smell to commit')

def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-V', '--verbose',
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
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to create code smell',
        parents=[parent_parser])

    subparser = parser.add_subparsers(title='subcommands', dest='command')

    subparser.required = True
    add_create_parser(subparsers, parent_parser)

    return parser

def do_create(args):
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = codeSmellClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        reponse = client.create(
            name, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create(
            name, auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url

def _get_keyfile(args):
    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser(~)
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)

def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
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
    else:
        raise codeSmellException("Invalid command: {}".format(args.command))

def main_wrapper():
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
