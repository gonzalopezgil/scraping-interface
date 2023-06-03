import unittest
import os
from gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
from scrapers.selenium_scraper import SeleniumScraper
import csv
from parameterized import parameterized

# TEST CASES

TEST_PARAMETERS = []

# 1. STATIC PAGE
url = 'https://webscraper.io/test-sites/tables'
column_titles = ['First Name', 'Last Name', 'Username']
xpaths = [
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "tables-all")]//div[contains(@class, "tables-semantically-correct")]//table//tbody//tr//td[2]',
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "tables-all")]//div[contains(@class, "tables-semantically-correct")]//table//tbody//tr//td[3]',
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "tables-all")]//div[contains(@class, "tables-semantically-correct")]//table//tbody//tr//td[4]'
]
selected_text = ['Mark', 'Otto', '@mdo']
pagination_xpath = None
max_pages = None
expected_count = 6

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

# 2. DYNAMIC PAGES (AJAX)
url = 'https://webscraper.io/test-sites/e-commerce/ajax/computers/tablets'
column_titles = ['Tablet', 'Reviews']
xpaths = [
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row ecomerce-items ecomerce-items-ajax")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "caption")]//h4//a[1]',
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row ecomerce-items ecomerce-items-ajax")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "ratings")]//p[1]'
]
selected_text = ['Lenovo IdeaTab', '12 reviews']
pagination_xpath = 'fake'
max_pages = 1
expected_count = 6

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

# 3. PAGINATION
url = 'https://webscraper.io/test-sites/e-commerce/static/computers/laptops'
column_titles = ['Computer', 'Description']
xpaths = [
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "caption")]//h4//a[1]',
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "caption")]//p[1]'
]
selected_text = ['Packard 255 G2', '15.6", AMD E2-3800 1.3GHz, 4GB, 500GB, Windows 8.1']
pagination_xpath = '/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/nav[1]/ul[1]/li[15]/a[1]'
max_pages = 20
expected_count = 6 * 19 + 3

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

# 4. SCROLLING
url = 'https://webscraper.io/test-sites/e-commerce/scroll/phones/touch'
column_titles = ['Phone', 'Price']
xpaths = [
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row ecomerce-items ecomerce-items-scroll")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "caption")]//h4//a[1]',
    '//html//body//div[contains(@class, "wrapper")]//div[contains(@class, "container test-site")]//div[contains(@class, "row")]//div//div[contains(@class, "row ecomerce-items ecomerce-items-scroll")]//div//div[contains(@class, "thumbnail")]//div[contains(@class, "caption")]//h4[1]'
]
selected_text = ['Nokia 123', '$24.99']
pagination_xpath = 'fake'
max_pages = 1
expected_count = 9

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

# 5. LOGIN
url = 'https://the-internet.herokuapp.com/secure'
column_titles = ['Message']
xpaths = [
    '//html//body//div[contains(@class, "row")]//div//div[contains(@class, "example")]//h4[1]',
]
selected_text = ['Welcome to the Secure Area. When you are done click logout below.']
pagination_xpath = 'fake'
max_pages = 1
expected_count = 1

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

# 6. CAPTCHA
url = 'https://www.google.com/recaptcha/api2/demo'
column_titles = ['Success']
xpaths = [
    '//html//body//div[contains(@class, "recaptcha-success")]'
]
selected_text = ['Se ha verificado correctamente… ¡Genial!']
pagination_xpath = 'fake'
max_pages = 1
expected_count = 1

TEST_PARAMETERS.append((url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count))

class IntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create one QApplication instance
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        # Initialize a MainWindow object
        self.main_window = MainWindow(self.app)

    @parameterized.expand(TEST_PARAMETERS)
    def test_thread_function(self, url, column_titles, xpaths, selected_text, pagination_xpath, max_pages, expected_count):
        # Test parameters
        file_name = 'test_file.csv'
        row = 0
        process_manager = self.main_window.process_manager
        for i, (xpath, text) in enumerate(zip(xpaths, selected_text)):
            process_manager.create_column(xpath)
            process_manager.set_first_text(i, text)
        signal_manager = self.main_window.signal_manager
        scraper = SeleniumScraper()
        if pagination_xpath:
            process_manager.pagination_xpath = pagination_xpath
            html = None
        else:
            driver = scraper.get_webpage(url)
            html = driver.page_source
            driver.quit()

        # Start the thread
        self.main_window.thread_function(url, column_titles, file_name, row, process_manager, signal_manager, None, html, max_pages=max_pages)

        # Check the file is saved correctly
        self.assertTrue(os.path.exists(file_name))

        # Open the CSV file and check its contents
        row_count = 0
        with open(file_name, 'r') as f:
            reader = csv.reader(f)

            # Check column headers
            headers = next(reader)
            self.assertEqual(headers, column_titles)

            # Check the format of the data
            for row in reader:
                self.assertEqual(len(row), len(column_titles))
                row_count += 1
        
        # Check the number of rows
        self.assertEqual(row_count, expected_count)

        # Remove the test file after the test
        os.remove(file_name)

if __name__ == '__main__':
    unittest.main()
