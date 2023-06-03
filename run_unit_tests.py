import unittest

loader = unittest.TestLoader()
test_suite = loader.discover('tests.scrapers')

test_runner = unittest.runner.TextTestRunner()
test_runner.run(test_suite)