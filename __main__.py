import sys
from lightbulb.lightbulb import LightBulb

def main(argv=sys.argv[1:]):
    myapp = LightBulb()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
