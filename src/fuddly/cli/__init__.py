#PYTHON_ARGCOMPLETE_OK
################################################################################
#
#  Copyright 2014-2016 Eric Lacombe <eric.lacombe@security-labs.org>
#
################################################################################
#
#  This file is part of fuddly.
#
#  fuddly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  fuddly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with fuddly. If not, see <http://www.gnu.org/licenses/>
#
################################################################################

import sys
import fuddly.cli.argparse_wrapper as argparse
import importlib

import argcomplete

# TODO script_argument_completer will be used once a sub-script argument completion logic is developped
from .run import get_scripts, script_argument_completer
# TODO tool_argument_completer will be used once a sub-script argument completion logic is developped
from .tool import get_tools, tool_argument_completer
from .show import get_projects

from typing import List
from fuddly.cli.error import CliException


def main(argv: List[str] = None):
    # This is done so you can call it from python shell if you want to
    # and give it parameters like:
    #
    #   main(["run", "some_script", "some", "important args"])
    #    or
    #   main("run some_script some important args")
    #
    #   This second for can not have space in the arguments, but so be it...
    #
    match argv:
        case None:
            argv = sys.argv[1:]
        case str():
            argv = argv.split(" ")

    parsers = {}
    arg_parser = parsers["main"] = argparse.ArgumentParser(
            prog="fuddly",
            description="the fuddly cli interface",
            epilog="use 'fuddly <action>' help more information on their arguments",
            exit_on_error=False
        )
    subparsers = arg_parser.add_subparsers(help="", dest="action", metavar="action")

    with subparsers.add_parser("shell", help="launch the fuddly interactive shell") as p:
        parsers["shell"] = p
        group = p.add_argument_group("Miscellaneous Options")
        group.add_argument(
            "-f",
            "--fmkdb",
            metavar="PATH",
            help="path to an alternative fmkDB.db. Create " "it if it does not exist.",
        )
        group.add_argument(
            "--external-display",
            action="store_true",
            help="display information on another terminal.",
        )
        group.add_argument(
            "--quiet",
            action="store_true",
            help="limit the information displayed at startup.",
        )

    with subparsers.add_parser("run", help="run a fuddly project script") as p:
        # XXX Should you be able to run script from outside the script dirs?
        parsers["run"] = p

        p.add_argument(
            "--ipython",
            action="store_true",
            help="tun the script using ipython",
        )

        p.add_argument(
            "script",
            metavar="script",
            help="name of the script to launch, the special value \"list\" list available scripts",
            choices=["list", *get_scripts()],
        )

        # TODO add arg completion for scripts
        p.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="arguments to pass through to the script",
        )  # .completer = script_argument_completer

    with subparsers.add_parser("new", help="create a new project or data model") as p:
        parsers["new"] = p
        p.add_argument(
            "--dest",
            metavar="PATH",
            type=argparse.PathType(
                dash_ok=False,
                type="dir"
            ),
            help="directory to create the object in.",
        )
        p.add_argument(
            "--pyproject",
            action="store_true",
            help="create a python package project structure"
        )
        p.add_argument(
            "object",
            choices=["dm", "data-model", "project:bare", "project:exemple"],
            metavar="object",
            help="type of object to create. [dm, data-model, project]",
        )
        p.add_argument(
            "name",
            help="name to give the create object.",
        )

    with subparsers.add_parser("tool", help="execute a fuddly tool") as p:
        parsers["tool"] = p
        p.add_argument(
            "tool",
            metavar="tool",
            help="name of the tool to launch, the special value \"list\" list available tools",
            choices=["list", *get_tools()],
        )
        # TODO add arg completion for tools
        p.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="arguments to passthrough to the tool",
            # TODO Add back when something is implemented
        )  # .completer = tool_argument_completer

    with subparsers.add_parser("workspace", help="manage fuddly's workspace") as p:
        parsers["workspace"] = p
        group = p.add_mutually_exclusive_group()
        group.add_argument(
            "--show",
            action="store_true",
            help="print the path to the workspace",
        )
        group.add_argument(
            "--clean",
            action="store_true",
            help="remove everything from the workspace",
        )

    with subparsers.add_parser("show", help="display the README file of a specified Project") as p:
        parsers["show"] = p
        group = p.add_argument_group("Miscellaneous Options")
        group.add_argument(
            "project",
            metavar="project",
            help="name of the project to show, the special value \"list\" list available projects",
            choices=["list", *map(lambda x: x[0], get_projects())],
        )


    # Needed because we set exit_on_error=False in the constructor
    try:
        argcomplete.autocomplete(arg_parser)
        args = arg_parser.parse_args(args=argv)
    except argparse.ArgumentError as e:
        print(e.message)
        print()
        arg_parser.print_help()
        return 0

    if args.action is None:
        arg_parser.print_help()
        return 0

    try:
        m = importlib.import_module(f"fuddly.cli.{args.action}")
        return m.start(args)
    except CliException as e:
        print(e.message)
        print()
        parsers[args.action].print_help()
        return 1
    except NotImplementedError:
        print("This function has not been implemented yet")
        return 1
