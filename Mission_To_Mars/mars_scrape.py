#!/usr/bin/env python
# coding: utf-8

# In[38]:


from splinter import Browser
from bs4 import BeautifulSoup
import time
import pandas as pd


# In[41]:


# https://splinter.readthedocs.io/en/latest/drivers/chrome.html
#!which chromedriver


# In[42]:


# URLs to Scrape
news_url = 'https://mars.nasa.gov/news'
image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
weather_url = 'https://twitter.com/marswxreport?lang=en'
facts_url = 'https://space-facts.com/mars/'
hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'


# In[43]:


# Make it easy to pass in a URL to lauch.
# Requires 'http://'
def launch(url):
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)


# In[37]:


# Create a function that opens a browser and grabs the soup

def scrape_url(url):
    # Set the Chrome Path and Launch the Browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    
    # Pass in a a URL to visit
    browser.visit(url)
    
    #give it a moment to load
    time.sleep(4)
    
    # Grab the HTML & Soup it!
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    
    browser.quit()
    
    return soup


# In[44]:


# Pass in the news url and return a list of dictionaries for the results

def get_news(url):
    
    # scrape the new url
    soup = scrape_url(url)
    
    # Get the News Slides from the Soup & Set up a Dictionary
    slides = soup.find_all('li',class_='slide')
    mars_news = []
    mars_dict = {}

    # Loop Through the Slides and Grap the Title and Teaser
    for x in range(len(slides)):
        title = slides[x].find('div', class_="content_title").text.replace("/n","")
        teaser = slides[x].find('div', class_="article_teaser_body").text.replace("/n","")

        # Add key, value pairs to dictionary
        post = {
            "title":title,
            "teaser":teaser,
        }

        #Get the list of dictionaries
        mars_news.append(post)

    return mars_news


# In[45]:


# Pass in the Mars Image Url and return the image path
def get_image(url):
    # grap the soup
    image_soup = scrape_url(url)
    
    #get the image path
    image_path = image_soup.find_all('a', class_='button fancybox')[0]['data-fancybox-href']
    full_image_path = f'https://www.jpl.nasa.gov{image_path}'
    return full_image_path


# In[7]:


# Pass in the weather url and return the text for the weather
def get_weather(url):

    soup = scrape_url(url)
    
    weather_full = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")[0].text
    weather = weather_full.split('pic.twitter')[0].replace('\n',"")
    return weather


# In[11]:


# Pass in the facts url and return a dataframe of the facts
def get_facts(url):
    tables = pd.read_html(url)
    return tables[0]


# In[25]:


# Pass in the Hemi url and return a list of urls to use for the next section
def get_links(url):
    base_url = 'https://astrogeology.usgs.gov'
    soup = scrape_url(url)
    items = soup.find_all(class_='item')
    links = []
    for i in items:
        links.append(f"{base_url}{i.find('a')['href']}")

    return links


# In[35]:



def get_hemi(url):
    # get list of urls from page
    base_url = 'https://astrogeology.usgs.gov'
    soup = scrape_url(url)
    items = soup.find_all(class_='item')
    links = []
    for i in items:
        links.append(f"{base_url}{i.find('a')['href']}")
                     
    # with each link, get titles & href
    hemi = []
    post = {}
    for link in links:
        soup = scrape_url(link)
        title = soup.find('h2', class_='title').text
        image_ref = soup.find_all('div', class_='downloads')[0].find_all('li')[0].a['href']

        post = {
            'title':title,
            'hemi_image_ref':image_ref
        }

        hemi.append(post)

    return hemi


# In[ ]:




