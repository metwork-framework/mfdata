import argparse
from xattrfile import XattrFile

DESCRIPTION = "get an attribute on a given file"


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('filepath',
                        help='Path of the file of which you want to print tags'
                        )
    parser.add_argument('name',
                        help='name of the tag'
                        )
    args = parser.parse_args()
    xaf = XattrFile(args.filepath)
    if args.name in xaf.tags:
        print(xaf.tags[args.name].decode('utf-8'))


if __name__ == '__main__':
    main()
