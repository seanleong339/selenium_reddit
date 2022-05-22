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

driver.get("https://www.reddit.com/r/singapore/")  # input reddit page or subreddit

#scroll down
scrolldown=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
for x in range(1):
    last_count = scrolldown
    time.sleep(3)
    scrolldown = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    
search_results = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "rpBJOHq2PR60pnwJlUyP0")))
currenturl = driver.current_url.split("/", 3)[-1]
print(currenturl)
download_path_page = "downloads/" + currenturl

posts = []
content = driver.page_source
soup = BeautifulSoup(content, "html.parser")
articles = soup.find_all("article")
links = []
for article in articles:
    links.append(article.find("a", {"data-testid": "post_timestamp"}).get("href"))
    
print(len(links))

for link in links:
    driver.get(link)
    time.sleep(5)
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    jsonsource = driver.get(link+'.json')
    jsonsource = driver.page_source
    jsonsoup = BeautifulSoup(jsonsource, 'html.parser')
    pagejson = jsonsoup.find('pre').get_text()
    pagejson = json.loads(pagejson)

    # create folder
    title = soup.find("h1").get_text().replace('/', '')
    download_path = download_path_page + "/" + title
    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    data = soup.find("div", {"data-test-id": "post-content"})
    user = data.find('a', {'data-click-id':'user'}).get_text()
    
    #Extract caption if exist
    maincaption = data.find_all('p')
    if maincaption is not None:
    	caption = ''
    	for caps in maincaption:
    		caption += caps.get_text()
    	
    #Store text info
    fulltext = {'Author':user, 'Caption':caption}
    
    #Extract lone img
    metacontent = soup.find('meta', {'property':'og:image'})
    if metacontent is not None:
    	metacontent = metacontent.get('content')
    	urllib.request.urlretrieve(metacontent, '{}/{}.jpg'.format(download_path,title))
    
    #Extract video if exist
    try:
    	videolink = pagejson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["dash_url"]
    	urllib.request.urlretrieve(videolink, '{}/{}.mp4'.format(download_path,'vid'))
    except Exception as e:
    	print("Video download failed with exception:")
    	print(e)
    
    #Extract img gallery if exist
    gallery = data.find('ul')
    if gallery is not None:
    	images = gallery.find_all('img')
    	count = 0
    	for image in images:
    		count += 1
    		link = image.get('src')
    		urllib.request.urlretrieve( link, '{}/{}({}).jpg'.format(download_path,'pic',count))
    		time.sleep(5)
    
    #Extract external link if exists
    external = data.find('a', {'data-testid':'outbound-link'})
    if external is not None:
    	externallink = external.get('href')
    	fulltext['External link'] = externallink
    	
    #Save text to JSON file 
    with open(os.path.join(download_path, 'text.json'), 'w') as file:
    	json.dump(fulltext, file, ensure_ascii=False, indent=4)
    
    time.sleep(3)
    	
