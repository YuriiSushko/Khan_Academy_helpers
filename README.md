# Setup Instructions

This document provides instructions on how to install the necessary packages and set up the environment for running the program.

## Prerequisites

Before you start, ensure you have the following installed:
- Python 3.x
- pip (Python package installer)

## Installing Packages

The program requires the following Python packages:
- `tqdm` for progress bars
- `colorama` for colored text output
- `selenium` for web browser automation

### Step-by-Step Installation

1. **Open your terminal or command prompt**.

2. **Install `tqdm`**:
    ```bash
    pip install tqdm
    ```

3. **Install `colorama`**:
    ```bash
    pip install colorama
    ```

4. **Install `selenium`**:
    ```bash
    pip install selenium
    ```

## Setting Up WebDriver

The program uses Selenium WebDriver to automate web browser actions. You need to download the appropriate WebDriver for your browser.

### Chrome WebDriver

1. **Download ChromeDriver**:
    - Visit the [ChromeDriver download page](https://googlechromelabs.github.io/chrome-for-testing/).
    - Download the version that matches your installed Chrome browser.

2. **Extract the downloaded file** and move it to a directory on your system.

3. **Add the directory containing `chromedriver` to your system PATH** or provide the full path in the script.

### Example Path Setup

In the script, replace `'chrome_driver_path'` with the actual path to the `chromedriver` executable. For example:
```python
chrome_driver_path = r'C:\ChromeDriver\chromedriver-win64\chromedriver.exe'
