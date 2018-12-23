from guichardin import extract
from dico import generate
import os
fixture_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")

def main():
    if not os.path.exists(fixture_dir):
        os.mkdir(fixture_dir)
    extract.main()
    generate.main()

if __name__ == '__main__':
    main()