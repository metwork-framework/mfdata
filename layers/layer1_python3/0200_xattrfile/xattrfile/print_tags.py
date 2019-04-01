import argparse
from xattrfile import XattrFile

DESCRIPTION = "print attributes of the given file"


def main():
    """
    Print attributes of the given file
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('filepath',
                        help='Path of the file of which you want to print tags'
                        )
    args = parser.parse_args()
    xaf = XattrFile(args.filepath)
    keys = sorted(xaf.tags.keys())
    for key in keys:
        print("%s = %s" % (key.decode('utf8'), xaf.tags[key].decode('utf8')))


if __name__ == '__main__':
    main()
