import time
import re
import json
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium_driver import driver

def login():
    # navigate to the application home page
    driver.get("https://www.mercadona.es/ns/entrada.php?js=1")
    username = driver.find_element_by_id("username")
    username.clear()
    username.send_keys(config["username"])
    password = driver.find_element_by_id("password")
    password.clear()
    password.send_keys(config["password"])
    username.submit()
    time.sleep(1)
    try:
        alert = driver.switch_to_alert().text
        return False
    except NoAlertPresentException:
        return True

def enter_search(term):
    current_handle = driver.current_window_handle
    driver.switch_to.window(current_handle)
    driver.switch_to.frame("toc")
    driver.switch_to.frame("topbusc")
    search_field = driver.find_element_by_id("busc_ref")
    search_field.clear()
    search_field.send_keys(term + Keys.ENTER)
    driver.switch_to.window(current_handle)
    driver.switch_to.frame("mainFrame")

def get_articles_from_current_page():
    articles = []
    html = driver.page_source
    pattern = re.compile("InsertaLinea\\((.*?)\\);")
    articleLineInfo = pattern.findall(html)
    for s in articleLineInfo:
        # 4th element is between double quotes and contains the text of the article
        # 5th element is the price and 13rd element contains price per kilogram
        p = re.compile("^.*?,.*?,.*?,\"(.*?)\",(.*?),.*?,.*?,.*?,.*?,.*?,.*?,.*?,\"(.*?)\"")
        m = p.search(s)
        if m:
            article = {}
            article['desc'] = m.group(1)
            article['price'] = m.group(2)
            article['kgPrice'] = m.group(3)
            articles.append(article)
        else:
            print("Could not get article from text: ", s)
    return articles

def get_num_results():
    num_results = 0
    string_containing_num_prod = driver.find_element_by_class_name("num_prod").text
    num_array = [int(s) for s in string_containing_num_prod.split() if s.isdigit()]
    if num_array:
        num_results = num_array[0]
    return num_results

def click_on_next():
    try:
        next_page = driver.find_element_by_id("NEXT")
        if next_page and next_page.is_displayed():
            next_page.click()
            time.sleep(2)
            return True
        return False
    except NoSuchElementException:
        return False

def search_by_term(term):
    articles = []
    enter_search(term)
    num_results = get_num_results()
    if num_results > 0:
        articles.extend(get_articles_from_current_page())
        while click_on_next():
            articles.extend(get_articles_from_current_page())
            if len(articles) == num_results:
                break
    return articles

# read config file
config = json.loads(open('config.json').read())
if login():
    term = input("what would you like to search? (Q to quit)")
    while (term != "Q"):
        articles = search_by_term(term)
        print("Found ", len(articles), " articles:\n", articles)
        term = input("Anything else to search? (Q=quit)")
else:
    print("Cannot login")

# close the browser
driver.quit()