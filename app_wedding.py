import time
import datetime
import logging
import pandas as pd
import requests
import io
import csv

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

start_time = time.time()
today = datetime.datetime.now().strftime("%Y-%m-%d")

# Read root keyword list from Google Sheet
googleSheet_PATH = ""

response = requests.get(googleSheet_PATH)
# response.encoding = 'utf-8'

assert response.status_code == 200, 'Wrong status code'

foo = response.content.decode('utf-8')
reader = csv.reader(io.StringIO(foo))
next(reader, None)

root_keywords = []
for row in reader:
    root_keywords.append(row[0])

print("The root keywords list: ", root_keywords)

# # Enter root keyword(s)
# root_keywords = ["性病檢測"]

def googleAutofill(root_keyword):
    suggested_kw = []

    # Chrome Driver path
    chromedriver_path = "WebDriver/chromedriver.exe"

    driver = webdriver.Chrome(executable_path=chromedriver_path)
    driver.get("http://www.google.com.hk")
    driver.maximize_window()

    # Find the search field
    search_field = driver.find_element_by_name('q')

    # Start to search: First round without space
    search_field.send_keys(root_keyword)
    try:
        autofill_1 = WebDriverWait(driver, 3).until(EC.visibility_of_all_elements_located((By.XPATH, "//form[@action='/search' and @role='search']//ul[@role='listbox']//li//span")))
        for item in autofill_1:
            suggested_kw.append(item.text)
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        pass

    time.sleep(3)
    try:
        search_field.clear()
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        pass

    # Search again: Second round with space
    search_field.send_keys(root_keyword + " ")
    try:
        autofill_2 = WebDriverWait(driver, 3).until(EC.visibility_of_all_elements_located((By.XPATH, "//form[@action='/search' and @role='search']//ul[@role='listbox']//li//span")))
        for item in autofill_2:
            # Only append new suggested queries
            if item.text in suggested_kw:
                pass
            else:
                suggested_kw.append(item.text)
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        pass

    driver.close()
    driver.quit()
    return suggested_kw

# Save as CSV file
def saveResults(df, savedpath, filename):
    print("Now saving file......")
    FILE = savedpath + filename
    with open(FILE, 'a+', encoding='utf-8') as f:
        df.to_csv(f, mode='a+', sep=',', encoding='utf-8', header=False, index=False)
    f.close()

# Start searching the autocomplete keywords
all_kw = []
for root_kw in root_keywords:
    print("\nSearching Root Layer: %s" % root_kw)
    l1_kw_list = googleAutofill(root_kw)
    print("\nRoot Layer Results: ", l1_kw_list)
    
    l1_kw_pos = 1
    for l1_kw in l1_kw_list:
        print("\nSearching Layer 1: %s" % l1_kw)
        l2_kw_list = googleAutofill(l1_kw)
        # print("\nLayer 1 Results: ", l2_kw_list)
        
        l2_kw_pos = 1
        for l2_kw in l2_kw_list:
            all_kw.append([root_kw, l1_kw, l1_kw_pos, l2_kw, l2_kw_pos, today])
            
            l2_kw_pos += 1
        l1_kw_pos +=1

# Columns: Root KW, L1 KW, L1 KW POS, L2 KW, L2 KW POS
results = pd.DataFrame(all_kw)

# Save results, append to existing data file
SAVEDPATH = ''
FILENAME = 'google_autofill_keywords_wedding.csv'
saveResults(df=results, savedpath=SAVEDPATH, filename=FILENAME)

# Record the execution time
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
print("---- Finished! %s minute %s second ----" %(m, s))

# Write log file
logging.basicConfig(filename='GoogleAutofill_Wedding_Log.txt', level=logging.DEBUG)
logging.debug("googleautofill wedding has been successfully run.")
logging.info(datetime.datetime.now())
logging.info("Finished scraping! %s minute %s second" %(m, s))