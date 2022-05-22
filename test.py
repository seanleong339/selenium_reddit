from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, urllib.request
import requests
import os
import json

WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

driver.get("https://www.reddit.com/r/singapore/")  #input reddit page or subreddit
search_results = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "rpBJOHq2PR60pnwJlUyP0")))

#scroll down
scrolldown=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
for x in range(1):
    last_count = scrolldown
    time.sleep(3)
    scrolldown = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    
content = driver.find_element(By.CLASS_NAME,"rpBJOHq2PR60pnwJlUyP0").get_attribute('outerHTML')
#with open('testing.txt', 'w') as file:
#    file.write(content)

posts = []
#content = driver.page_source
soup = BeautifulSoup(content, "html.parser")
articles = soup.find_all("article")
links = []
for article in articles:
    links.append(article.find("a", {"data-testid": "post_timestamp"}).get("href"))
    
print(len(links))