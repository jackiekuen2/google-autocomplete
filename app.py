import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

# Chrome Driver path
chromedriver_path = "WebDriver/chromedriver"
# options = ChromeOptions()
# options.add_argument('--kiosk')

driver = webdriver.Chrome(executable_path=chromedriver_path)
driver.get("http://www.google.com.hk")
driver.maximize_window()

# Find the search field
search_field = driver.find_element_by_name('q')

# Enter root keyword(s)
root_keyword = "Hong Kong"
searchQuery_googleAutofill = []

search_field.send_keys(root_keyword)
autofill_1 = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//form[@action='/search' and @role='search']//ul[@role='listbox']//li//span")))
for item in autofill_1:
    searchQuery_googleAutofill.append(item.text)

time.sleep(3)
search_field.clear()

search_field.send_keys(root_keyword + " ")
autofill_2 = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//form[@action='/search' and @role='search']//ul[@role='listbox']//li//span")))
for item in autofill_2:
    searchQuery_googleAutofill.append(item.text)

driver.close()
driver.quit()

# De-duplicate keyword list
searchQuery_googleAutofill = set(searchQuery_googleAutofill)

for keyword in searchQuery_googleAutofill:
    print(keyword)
