import sys


def mappath(f):
    filepath = f.split('/', 1)[1]
    return f'file {filepath}'


files = map(mappath, sys.argv[1:])
print('\n'.join(files))
