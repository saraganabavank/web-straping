from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import pandas as pd 
import logging

# Chrome webdriver  Set up 
driver = webdriver.Chrome()

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

data = []  
completedUrls = []
 
#  Get all linkes in a class
def getLinksByClass(url, class_name):
    try:
        # Open URL in the browser
        driver.get(url)
        # Target particular parant tags by class name
        target_div = driver.find_element(By.CLASS_NAME, class_name)

        # Find all <a> tags within the parent tags
        urls = target_div.find_elements(By.TAG_NAME, 'a')  


    except Exception as e: 
        logger.error(f"An error occurred: {str(e)}")

    finally:
        return urls

# strap data form html page
def collectPageData(url):
    result  = []
    try:
        logger.info(f"Opened URL: {url}")
        driver.get(url)

        # import time
        # time.sleep(5)

        # Get the page source
        page_source = driver.page_source

        # Parse HTML
        soup = BeautifulSoup(page_source, 'html.parser') 

        # Extract data from the page  
        for article in soup.find_all('article'): 
            title = article.find('h6')
            title = title.text  if title else ''
            title = title.strip()  if title else '' 

            date = article.find('span')  
            date = date.text  if date else ''
            date = date.strip()  if date else ''

            link = article.find('a')
            link = link.get('data-bg') if link else ''
            link = link.strip()  if link else ''

            like = article.find_next('span')
            like = like.find_next('span') if like else ''
            like = like.find_next('span') if like else ''
            like = like.find_next('span') if like else ''

            #Append data to the array
            result.append({'Blog': title, 'Blog Date': date, 'Blog Image URL': link,'Like Count':like})
    except Exception as e: 
        logger.error(f"An error occurred: {str(e)}") 
    return result

# Find the next page 
def getNextPage(urls):
    for link in urls:
            href = link.get_attribute('href')
            if href  and href not in completedUrls:
                return href
    return ''

# main
def main(url): 
    # Extract data
    pagaData = collectPageData(url)
    # Push to a array
    data.extend(pagaData)
    # Mark the url as processed
    completedUrls.append(url)
    # Get all possible links in html page's pagination section 
    links = getLinksByClass(url,'pagination')
    # get the next unpricessed page
    url = getNextPage(links)

    if len(url)>0 : 
        main(url)
    # Close the browser session
    else :   
        driver.quit()
        logger.info("Browser session closed")
        # Create a DataFrame from the list
        df = pd.DataFrame(data)
        # Write the DataFrame to CSV file
        df.to_csv('output.csv', index=False)
        logger.info("Data write into  output.csv.")

# Define the base URL
base_url = 'https://rategain.com/blog/'


main(base_url) 

 