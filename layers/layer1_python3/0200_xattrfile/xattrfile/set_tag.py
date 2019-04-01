import argparse
from xattrfile import XattrFile

DESCRIPTION = "set an attribute on a given file"


def main():
    """
    Set an attribute on a given file
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('filepath',
                        help='Path of the file of which you want to print tags'
                        )
    parser.add_argument('name',
                        help='name of the tag'
                        )
    parser.add_argument('value',
                        help='value of the tag'
                        )
    args = parser.parse_args()
    xaf = XattrFile(args.filepath)
    xaf.tags[args.name] = args.value
    xaf.commit()


if __name__ == '__main__':
    main()
