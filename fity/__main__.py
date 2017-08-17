#!/usr/bin/env python

import sys
import fity


def inspect_path(path, list_archives=False):
    with open(path, 'r') as file:
        try:
            filetype = fity.detect(file)
        except fity.DetectionError as e:
            print(type(e).__name__)
            return False
        else:
            print('  description: %s' % filetype.description)
            print('  extension: %s' % filetype.extension)
            print('  mimetype: %s' % filetype.mimetype)
            for key, value in filetype.properties.items():
                print('  %s: %s' % (key, value))
            if list_archives:
                if isinstance(filetype, fity.ArchiveType):
                    with filetype.open_archive() as archive:
                        print(archive.describe(indent=2))
            return True


def main(argv):
    if len(sys.argv) == 1:
        sys.exit('Usage: %s [-a] [paths]' % sys.argv[0])
    paths = sys.argv[1:]
    if paths[0] == '-a':
        list_archives = True
        paths = paths[1:]
    else:
        list_archives = False
    count = 0
    successes = 0
    for path in paths:
        print(path)
        count += 1
        if inspect_path(path, list_archives):
            successes += 1
        print('')
    print('Total files found: %d' % count)
    print('Recognized: %d' % successes)
    print('Unrecognizable: %d' % (count - successes))


if __name__ == '__main__':
    main(sys.argv)
