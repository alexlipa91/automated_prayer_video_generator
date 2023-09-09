from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("detach", True)

userdatadir = '/Users/alessandrolipa/Library/Application Support/Google/Chrome'
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument(f"user-data-dir={userdatadir}")
options.add_argument("profile-directory=Profile 1")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = webdriver.Chrome(options=options)
driver.get("https://www.youtube.com")
