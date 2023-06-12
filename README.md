# Scraping Interface
![icon](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/85e24aff-f89d-4d58-af3c-6b4b8c8fb045)

The Scraping Interface project is a cross-platform desktop application developed using Python and the PyQt5 library. It provides a user-friendly interface for web scraping, allowing users to extract information from web pages easily.

## ✨ Features

- **Web Scraping**: Extract online data using a browser-like interface.
- **Dynamic Browsing**: Browse the web with Chromium and perform standard actions like navigation, page reloads and searching.
- **XPath Selection**: Highlight and select elements on web pages using generalized XPath expressions.
- **Table Preview**: Select data from sites and view it in a table format for easy extraction.
- **Pagination Support**: Extract data from multiple pages with consistent structures, including automatic handling of pagination buttons.
- **Data Export**: Save scraped data in popular formats such as Excel, CSV, JSON, or XML.
- **Template Management**: Save and load scraping configurations for reuse, allowing quick access to previously configured selections.
- **Authentication Support**: Securely store and use encrypted login credentials to access authenticated web pages.
- **CAPTCHA Handling**: Solutions to handle CAPTCHA-protected pages for uninterrupted data extraction.
- **Process Monitoring**: Track and manage scraping processes with progress indicators about the ongoing tasks.

## 🚀 Installation

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

## 🛠️ Usage

1. Launch the application, and you will be presented with a user-friendly interface with four tabs: Home, Browser, Processes and Settings.
![Home](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/7a0e93e6-335c-4f8c-9aea-4eed7f896819)
2. Use the browser tab to navigate, search and interact with sites.
![Browser](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/7491e89c-048e-492d-a42e-703d147a2edc)
3. When you're ready to extract data, navigate to the desired web page and click the "Scrape" button. The program will display the extracted data in a table for preview.
![BrowserScraping](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/a0678460-5e65-4707-9339-2f03bf87d2df)
4. Customize your selection using generalized XPath expressions and modify the table as needed.
![BrowserSelection](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/6c82cca4-4583-4baa-b6be-b82d5e141282)
5. Configure pagination settings, save templates for future use, and choose the desired data export format in the respective process.
![BrowserPagination](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/7511f2c9-92a6-40dc-91c2-79ef899a6be3)
6. Monitor the scraping processes in the Processes tab, and manage them by starting, stopping, or opening the output files.
![Processes](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/c8519d47-5f04-4c74-95f6-067c8b0748d4)
7. Adjust application settings, including browser preferences and language management in the Settings tab.
![Settings](https://github.com/gonzalopezgil/scraping-interface/assets/74659017/d32409d6-2b55-4f62-a6e6-80a79c38f448)

## :octocat: Contributing

Contributions to the Scraping Interface project are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## 📃 License

This project is licensed under the [MIT License](https://opensource.org/license/mit/). Feel free to use, modify, and distribute the code.
