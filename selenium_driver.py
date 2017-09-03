import os
from selenium import webdriver

# get the path of ChromeDriverServer
dir = os.path.dirname(__file__)
chrome_driver_path = dir + "\chromedriver.exe"
# create a new Chrome session
driver = webdriver.Chrome(chrome_driver_path)
driver.implicitly_wait(10)
driver.maximize_window()

