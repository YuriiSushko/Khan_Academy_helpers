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

In the ScrappingApplicationRunner.py, replace `'chrome_driver_path'` with the actual path to the `chromedriver` executable. For example:
```python
chrome_driver_path = r'C:\ChromeDriver\chromedriver-win64\chromedriver.exe'
```

# Run instructions
## Start Chrome with Remote Debugging

Before running the program, you need to start Chrome with remote debugging enabled. Open your command prompt and execute the following commands:
```bash
cd "C:\Program Files\Google\Chrome\Application"
```
- **This is the path to Chrome.exe**: This is where Chrome is installed on your system. Adjust the path if Chrome is installed in a different location.
```bash
.\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfile"
```

## Open Chrome Browser
1. **Ensure Only One Window Is Open**
   Make sure that only one window of Chrome is open after starting it with the remote debugging port. Having multiple windows can cause issues with the WebDriver connection.

2. **Log In to Crowdin**
    - Navigate to Crowdin and log in if you haven't done so already. This step is necessary only for the first time.

3. **Select the Right View**
   - Choose the "Side by Side" view.
   - Ensure that all progress options are selected to view and manage translations effectively.
      
## Run the ScrapingApplicationRunner.py
