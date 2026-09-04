import unittest

from statskit import median


class MedianTest(unittest.TestCase):
    def test_odd_length(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_even_length(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_unsorted_even(self):
        self.assertEqual(median([10, 2, 8, 4]), 6.0)


if __name__ == "__main__":
    unittest.main()
