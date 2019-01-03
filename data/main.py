from guichardin import extract
from dico import generate
import argparse
import os
fixture_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")

def main():
    if not os.path.exists(fixture_dir):
        os.mkdir(fixture_dir)
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", help="force decoding", action="store_true")
    args = parser.parse_args()
    extract.main(args.force)
    generate.main(args.force)

if __name__ == '__main__':
    main()
