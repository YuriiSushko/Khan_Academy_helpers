from ScrappingApplication import ScrappingApplication

if __name__ == "__main__":
    chrome_driver_path = r'C:\ChromeDriver\chromedriver-win64\chromedriver.exe'
    app = ScrappingApplication(chrome_driver_path)
    if app.webdriver_installed:
        app.run()
    else:
        print("Please install and configure the WebDriver correctly to run this application.")
