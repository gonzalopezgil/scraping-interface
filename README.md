# Scraping Interface

The Scraping Interface project is a cross-platform desktop application developed using Python and the PyQt5 library. It provides a user-friendly interface for web scraping, allowing users to extract information from web pages easily.

## Features

- **Web Scraping**: Extract data from web pages using a browser-like interface.
- **Dynamic Browsing**: Browse the web with Chromium and perform standard browser actions like navigation, page reloads, and searching.
- **XPath Selection**: Highlight and select elements on web pages using generalized XPath expressions.
- **Table Preview**: View and select data from web pages in a table format for easy extraction.
- **Pagination Support**: Extract data from multiple pages with consistent structures, including automatic handling of pagination buttons.
- **Data Export**: Save scraped data in popular formats such as Excel, CSV, JSON, or XML.
- **Template Management**: Save and load scraping configurations for reuse, allowing quick access to previously configured selections.
- **Authentication Support**: Securely store and use encrypted login credentials to access authenticated web pages.
- **Process Monitoring**: Track and manage scraping processes with progress indicators and detailed information about the ongoing tasks.

## Installation

### From Source

To install and run the Scraping Interface application from source, follow these steps:

1. Clone the repository:

```shell
git clone https://github.com/gonzalopezgil/scraping-interface.git
```

2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

3. Run the application:

```shell
python main.py
```

### Using Pre-built Executables

You can also use pre-built executables for your operating system. Download the appropriate release from the [Releases](https://github.com/gonzalopezgil/scraping-interface/releases) page of this repository. Select the version compatible with your operating system (Windows, MacOS, or Linux) and follow the installation instructions provided in the release.

## Usage

1. Launch the application, and you will be presented with a user-friendly interface with four tabs: Home, Browser, Processes and Settings.
2. Use the browser tab to navigate the web, perform searches, and interact with web pages.
3. When you're ready to extract data, navigate to the desired web page and click the "Scrape" button. The program will display the extracted data in a table for preview and selection.
4. Customize your selection using generalized XPath expressions and modify the table as needed.
5. Configure pagination settings, save templates for future use, and choose the desired data export format in the respective tabs.
6. Monitor the scraping processes in the Processes tab, and manage them by starting, stopping, or opening the output files.
7. Adjust application settings, including browser preferences and password management, in the Settings tab.

## Contributing

Contributions to the Scraping Interface project are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit/). Feel free to use, modify, and distribute the code.