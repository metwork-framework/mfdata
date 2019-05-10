#!/usr/bin/env python3

import os
import argparse
import time
from mflog import get_logger

LOGGER = get_logger("generate_random_files.py")


def iteration(nb_files, prefix, size):
    time1 = time.time()
    for i in range(nb_files):
        with open('%s%i' % (prefix, i), 'wb') as f:
            f.write(os.urandom(size))
    time_spent = time.time() - time1
    LOGGER.info("time to generate %i files of size %i: %f s" % (nb_files,
                                                                size,
                                                                time_spent))
    time_to_sleep = 1. - time_spent
    if time_to_sleep < 0.:
        LOGGER.warning("more than 1 second to generate %i files" % size)
    else:
        time.sleep(time_to_sleep)


def main():
    parser = argparse.ArgumentParser("Create n files of size m per second")
    parser.add_argument("--nb_files", type=int,
                        help="nb files to create (default=1000) each second",
                        default=1000)
    parser.add_argument("--size", type=int,
                        help="size of the files to create (default=1000)",
                        default=1000)
    parser.add_argument("--prefix", type=str,
                        help="prefix for files name (default='file')",
                        default="file")
    parser.add_argument("--seconds", type=int,
                        help="number of iterations (default: 60)",
                        default=60)

    args = parser.parse_args()
    for it in range(0, args.seconds):
        LOGGER.info("Iteration: %i", it)
        iteration(args.nb_files, args.prefix, args.size)


if __name__ == "__main__":
    main()
