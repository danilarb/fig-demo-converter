import time
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import helpers

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode

driver = selenium.webdriver.Chrome(options=chrome_options)
driver.get(helpers.CROP_URL)
driver.implicitly_wait(10)

email_input = driver.find_element(By.ID, 'email')
email_input.send_keys(helpers.USER_NAME)

next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
next_button.click()

pass_input = driver.find_element(By.ID, 'password')
pass_input.send_keys(helpers.PASSWORD)

login_button = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
login_button.click()

time.sleep(10)

summary_list = driver.find_element(By.XPATH, "//div[contains(text(), 'Costs & Other Income')]")
summary_list.click()

activity_list_list = driver.find_elements(By.CLASS_NAME, 'activity-list')

for activity_list in activity_list_list:
    time.sleep(2)
    activity_list.click()

activity_details = driver.find_elements(By.CLASS_NAME, 'activity-line-row')
print(activity_details)

details = []

for activity_detail in activity_details:
    print(activity_detail.text)
    detail = activity_detail.text.split('\n')
    try:
        if activity_detail.find_element(By.CLASS_NAME, 'status-future'):
            detail.append('forecast')
            print('forecast')
    except selenium.common.exceptions.NoSuchElementException:
        try:
            if activity_detail.find_element(By.CLASS_NAME, 'status-current'):
                detail.append('actuals')
                print('actuals')
        except selenium.common.exceptions.NoSuchElementException:
            detail.append('not found')
            print('not found')
    details.append(detail)

driver.quit()

for detail in details:
    if len(detail) == 6:
        detail = {
            ''
        }

time.sleep(30)

# html_content = driver.page_source

# soup = BeautifulSoup(html_content, 'html.parser')

# with open('crops.html', 'w', encoding='utf-8') as file:
#     file.write(soup.prettify())

