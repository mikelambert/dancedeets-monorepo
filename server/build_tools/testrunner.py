#!/usr/bin/python

import argparse
import sys
import unittest

from dancedeets import runner


def main(test_path, test_pattern):
    # Discover and run tests.
    suite = unittest.loader.TestLoader().discover(test_path, test_pattern)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    runner.setup()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--test-path', help='The path to look for tests, defaults to the current directory.', default='.')
    parser.add_argument('--test-pattern', help='The file pattern for test modules, defaults to *_test.py.', default='*_test.py')

    args = parser.parse_args()

    result = main(args.test_path, args.test_pattern)

    if not result.wasSuccessful():
        sys.exit(1)
