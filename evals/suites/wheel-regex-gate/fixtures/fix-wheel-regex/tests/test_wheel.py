"""Frozen tests for packaging.utils.parse_wheel_filename.

Inputs are taken verbatim from packaging's own test_utils.py. The invalid case
"foo\\n-1.0-py3-none-any.whl" is the one this bug lets through: a trailing
newline in the project name must be rejected, and the buggy regex accepts it.
Written in stdlib unittest so the demo needs no test-runner install.
"""
import unittest

from packaging.utils import InvalidWheelFilename, parse_wheel_filename
from packaging.version import Version

VALID = [
    ("some_PACKAGE-1.0-py3-none-any.whl", "some-package", Version("1.0"), ()),
    ("foo-1.0-1000-py3-none-any.whl", "foo", Version("1.0"), (1000, "")),
    ("foo-1.0-1000abc-py3-none-any.whl", "foo", Version("1.0"), (1000, "abc")),
]

INVALID = [
    "foo-1.0.whl",                       # missing tags
    "foo-1.0-py3-none-any.wheel",        # wrong extension
    "foo__bar-1.0-py3-none-any.whl",     # invalid name (__)
    "foo\n-1.0-py3-none-any.whl",        # invalid name (trailing newline)
    "foo#bar-1.0-py3-none-any.whl",      # invalid name (#)
    "-1.0-py3-none-any.whl",             # empty project name
    "foobar-1.x-py3-none-any.whl",       # invalid version
    "foo-1.0-abc-py3-none-any.whl",      # build number not starting with a digit
    "foo-1.0-200-py3-none-any-junk.whl", # too many dashes
    "foo-1.0--none-any.whl",             # empty interpreter component
    "foo-1.0-py3-none-.whl",             # empty platform component
]


class ParseWheelFilenameTest(unittest.TestCase):
    def test_valid_filenames(self):
        for filename, name, version, build in VALID:
            with self.subTest(filename=filename):
                got_name, got_version, got_build, _tags = parse_wheel_filename(filename)
                self.assertEqual(got_name, name)
                self.assertEqual(got_version, version)
                self.assertEqual(got_build, build)

    def test_invalid_filenames_are_rejected(self):
        for filename in INVALID:
            with self.subTest(filename=filename):
                with self.assertRaises(InvalidWheelFilename):
                    parse_wheel_filename(filename)


if __name__ == "__main__":
    unittest.main()
