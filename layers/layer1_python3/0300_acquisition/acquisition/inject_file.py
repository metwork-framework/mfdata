#!/usr/bin/env python3

import sys
import os
import argparse
from xattrfile import XattrFile
from mflog import getLogger
from mfutil import get_unique_hexa_identifier
from acquisition.utils import get_plugin_step_directory_path


logger = getLogger("mfdata.reinject_plugin_step")


def main():
    parser = argparse.ArgumentParser("Inject a file into a plugin/step")
    parser.add_argument("filepath", type=str, help="filepath to inject")
    parser.add_argument("--plugin", type=str,
                        help="plugin name (default :switch)",
                        default="switch")
    parser.add_argument("--step", type=str,
                        help="step name (default: main)",
                        default="main")
    parser.add_argument("--move", action="store_true",
                        help="move the file instead of copying it "
                        "(default: copy)")
    parser.add_argument("--random-basename", action="store_true",
                        help="use a random basename for copying/moving "
                        "the file (default: keep the original basename)")
    parser.add_argument("--incoming", action="store_true",
                        help="ignore plugin and step parameter and inject "
                        "the file into the first configured directory listened"
                        " by the switch plugin")

    args = parser.parse_args()
    try:
        x = XattrFile(args.filepath)
    except Exception:
        logger.warning("can't open %s" % args.filepath)
        sys.exit(1)
    if args.random_basename:
        basename = get_unique_hexa_identifier()
    else:
        basename = os.path.basename(args.filepath)
    if args.incoming:
        env_var = 'MFDATA_INTERNAL_PLUGINS_SWITCH_DIRECTORIES'
        first_directory = os.environ[env_var].split(';')[0]
        new_filepath = os.path.join(os.environ['MFDATA_DATA_IN_DIR'],
                                    first_directory, basename)
    else:
        new_filepath = \
            os.path.join(get_plugin_step_directory_path(args.plugin,
                                                        args.step), basename)
    if args.move:
        res, moved = x.move_or_copy(new_filepath)
        if not res:
            logger.warning("can't move %s to %s" % (args.filepath,
                                                    new_filepath))
            sys.exit(1)
    else:
        res = x.copy_or_nothing(new_filepath)
        if not res:
            logger.warning("can't copy %s to %s" % (args.filepath,
                                                    new_filepath))
            sys.exit(1)


if __name__ == "__main__":
    main()
