import requests
import pandas as pd
import time
import pymongo
from bs4 import BeautifulSoup as bs
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

db = client.mars_db

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()
    

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'


    # Retrieve page with the requests module
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')


    # Examine the block of result, then determine element that contains sought info
    results = soup.find_all('div',class_='slide')

    # return the title of the news
    news_title = soup.find('div', class_='content_title').text

    # return the paragraph of the news
    news_p = soup.find('div', class_='rollover_description_inner').text    

    

    # URL of the page to be scraped
    jpl_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(jpl_image_url)

    html = browser.html
    soup = bs(html, "html.parser")
    featured_image_url = soup.find('div', class_="object-cover").find('img')['src']


    # results = soup.find_all('figure', class_="lede")

    # for result in results:
    #     image = result.a['href']
    #     featured_image_url = "https://www.jpl.nasa.gov"+ image


    # URL from Mars Facts webpage
    mars_url = 'https://space-facts.com/mars/'


    # Read from URL
    mars_table = pd.read_html(mars_url)
   
    mars_df = mars_table[0]

    # Change the columns name
    mars_df.columns = ['Description','Value']

    # Set the index to the `Description` column 
    mars_df.set_index('Description', inplace=True)

    # Save the HTML file
    mars_df = mars_df.to_html('mars_html')
    

    # Visit hemispheres website through splinter module 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'


    # Retrieve page with the requests module
    response = requests.get(hemispheres_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, "html.parser")

    # Retreive all items that contain mars hemispheres information
    items = soup.find_all('div', class_='item')

    # Create empty list for hemisphere urls 
    hemisphere_image_urls = []


    # Store to regular url 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'

    # Loop through the items previously stored
    for x in items: 
        # Store title
        title = x.find('h3').text
        
        # Store link that leads to full image website
        partial_img_url = x.find('a', class_='itemLink product-item')['href']
        
        # Visit the link that contains the full image website 
        browser.visit(hemispheres_main_url + partial_img_url)
        
        # HTML Object of individual hemisphere information website 
        partial_img_html = browser.html
        
        # Parse HTML with Beautiful Soup for every hemisphere site
        soup = bs( partial_img_html, 'html.parser')
        
        # Extracting the full image 
        img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
        print(img_url)
        
        # Append the link and title to the empty link created at the beginning 
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
        

    # Display hemisphere_image_urls
    hemisphere_image_urls
    output = {"news_title": news_title, "news_para": news_p, 
    "image_url": featured_image_url,
     "html_fact": mars_df, "hemisphere_url": hemisphere_image_urls }

    browser.quit()
    return output
print(scrape_info())