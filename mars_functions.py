#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -----//  GREETING  //---------------------------------------
print("You imported Mike's Mars Functions.  Let's Blast Off!")
# ------------------------------------------------------------


# In[ ]:


# -----//  DEPENDENCIES  //---------------------------------------
# ----------------------------------------------------------------

from splinter import Browser
from bs4 import BeautifulSoup
import time
import pandas as pd
from IPython.display import Image

import flask as fl
import pymongo


# In[ ]:


# -----//  URLS  //-----------------------------------------------
# ----------------------------------------------------------------
# URLs to Scrape
news_url = 'https://mars.nasa.gov/news'
image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
weather_url = 'https://twitter.com/marswxreport?lang=en'
facts_url = 'https://space-facts.com/mars/'
hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
blast_off_image = 'https://idb-fac2.mgxcdn.ru/2017/02/26/cover/a1e2e1941ad06ac46dd6160c273335f0-tom-and-jerry-blast-off-to-mars.jpg'


# In[ ]:


# -----//  GENERIC BROWSER FUNCTIONS  //--------------------------
# ----------------------------------------------------------------
# Make it easy to pass in a URL to lauch.
# Requires 'http://'
def launch(url):
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)
    return browser


# Create a function that opens a browser and grabs the soup
def scrape_url(url):
    # -------
    print("Gonna launch a browser to get info.  In 3... 2... 1...")
    browser = launch(url)    
    # -------
    
    #give it a moment to load
    time.sleep(3)
    # -------
    # Grab the HTML & Soup it!
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    
    browser.quit()
    
    return soup

#-------/ QUICK TIMESTAMP /----------------------
def ts():
    timestamp = time.strftime('%y%m%d%H%M%s')
    date = time.strftime('%b-%d-%Y')
    return timestamp, date


# In[ ]:


#-----/ CONNECT TO MONGO /---------------------
#----------------------------------------------

def connect_mongo():
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    #print(f"You're connected! Passing back the client.")
    return client

#-----/ CREATE COLLECTION /---------------------

def mongo_me(db,col):
    client = connect_mongo()
    collection = client[db][col]
    #print(f"You're connected to DB:{db} | Collection:{col}")
    return collection

def mars_mongo(dict,collection_name):
    
    # setup mongo connection
    db = 'mission_to_mars'
    collection = mongo_me(db,collection_name)
    
    # insert item into mars db
    collection.insert_many(dict)
    print(f""" 
        
        Mango, Mongo...DONE!
        DB: {db} | Collection: {collection_name}
        ------------------------------------------------
        return: collection string to find, query, etc.
       
    """)
    
    return collection


#-----/ COMMON MONGO FUNCTIONS /---------------------

def last_doc(collection):
    last = collection.estimated_document_count()-1
    print(f"This collection has {last+1} documents.  Passing back the last one...(without the '_id')")
    return collection.find({},{'_id':0})[last]

def drop(db_name):
    client = connect_mongo()
    client.drop_database(db_name)
    return client.list_database_names()


# In[ ]:


# -----//  SPECIFIC MARS SCRAPE FUNCTIONS  //---------------------
# ----------------------------------------------------------------

def mars_news():
    
    print(f'Getting News from {news_url}')
    
    # scrape the new url
    soup = scrape_url(news_url)
    
    # Get the News Slides from the Soup & Set up a Dictionary
    slides = soup.find_all('li',class_='slide')
    my_list = []    
    counter = 0

    #>> Loop Through the Slides and Grap the Title and Teaser
    print('...looping through slides to get title & teaser.')
    for x in range(len(slides)):
        counter += 1
        title = slides[x].find('div', class_="content_title").text.replace("/n","")
        teaser = slides[x].find('div', class_="article_teaser_body").text.replace("/n","")

        # Add key, value pairs to dictionary
        post = {
            "title":title,
            "teaser":teaser,
            "timestamp":ts()[0],
            "date":ts()[1]
        }

        #Get the list of dictionaries
        my_list.append(post)
    ##>> End For Loop
  
    print(f'All set!  You got the news as a list of {counter} dictionaries.')
    
    # Drop the News Collection
    my_db = 'mission_to_mars'
    my_col = 'news'
    mongo_me(my_db,my_col).drop()
    
    # Insert the list of News articles into the MongoDB
    collection = mars_mongo(my_list,my_col)
    return collection


# In[ ]:


# -----//  GET THE MARS HEADLINE IMAGE  //---------------------
# Pass in the Mars Image Url and return the image path
def mars_image():
    
    print(f'Getting Image from {image_url}')
    
    # grap the soup
    image_soup = scrape_url(image_url)
    print('openning the url to grab the image.')
    
    #get the image path
    image_path = image_soup.find_all('a', class_='button fancybox')[0]['data-fancybox-href']
    image_desc = image_soup.find_all('a', class_='button fancybox')[0]['data-description']
    full_image_path = f'https://www.jpl.nasa.gov{image_path}'
        
    # Create the Post
    post = {
            "date":ts()[1],
            "timestamp":ts()[0],
            "image_desc":image_desc,
            "image":full_image_path
        }
    
    
    # Insert into Mongo
    my_db = 'mission_to_mars'
    my_col = 'images'
    collection = mongo_me(my_db,my_col)
    collection.insert_one(post)
    
    return collection

def show_mars():
    collection = mongo_me('mission_to_mars','mars_images')
    doc = last_doc(collection)
    image = doc['image']
    text = doc['image_desc']
    print(text)
    return Image(url=image)


# In[ ]:


# -----//  GET THE MARS WEATHER  //---------------------
# Pass in the weather url and return the text for the weather
def mars_weather():
    
    print(f'Getting Weather from {weather_url}')
    
    post_weather = {}
    
     # grap the soup
    soup = scrape_url(weather_url)
    
    weather_full = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")[0].text
    weather = weather_full.split('pic.twitter')[0].replace('\n',"")
    
    # Add key, value pairs to dictionary
    post = {
            "date":ts()[1],
            "timestamp":ts()[0],
            "weather":weather
        }

    
    # Insert into Mongo
    my_db = 'mission_to_mars'
    my_col = 'weather'
    collection = mongo_me(my_db,my_col)
    collection.insert_one(post)
    
    return collection


# In[ ]:


# -----//  GET THE MARS FACTS  //---------------------
# Pass in the facts url and return a dataframe of the facts
def mars_facts():
    
    print(f'Getting Facts from {facts_url}')
    print('Getting the tables...')
    print('Easy.  As.  Py.')
    tables = pd.read_html(facts_url)
    
    post = {
        
        "date":ts()[1],
        "timestamp":time.strftime("%Y%m%d%H%M%S", time.gmtime()),
        "table_html":tables[0].to_html()
    
    }
    
    # Insert into Mongo
    my_db = 'mission_to_mars'
    my_col = 'facts'
    collection = mongo_me(my_db,my_col)
    collection.insert_one(post)
    
    return collection, tables[0]


# In[ ]:



# -----//  GET THE HEMISPHERE LINKS  //---------------------
# Pass in the Hemi url and return a list of urls to use for the next section
def get_hemi_links():
    
    print(f'Getting links from {hemi_url}')
    
    base_url = 'https://astrogeology.usgs.gov'
    soup = scrape_url(hemi_url)
    items = soup.find_all(class_='item')
    links = []
    for i in items:
        links.append(f"{base_url}{i.find('a')['href']}")

    return links



# -----//  GET THE LINKS AND HEMISPHERE IMAGES  //---------------------
def mars_hemi():
    # get list of urls from page
    links = get_hemi_links()
    print("Got the links!  Let's grab the images!")
                     
    # with each link, get titles & href
    my_list = []
    post = {}
    for link in links:
        print(f'Getting images from {link}')
        soup = scrape_url(link)
        title = soup.find('h2', class_='title').text
        image_ref = soup.find_all('div', class_='downloads')[0].find_all('li')[0].a['href']

        post = {
            'title':title,
            'hemi_image_ref':image_ref
        }

        my_list.append(post)
    
                     
    # Insert into Mongo
    my_db = 'mission_to_mars'
    my_col = 'hemispheres'
    collection = mongo_me(my_db,my_col)
    collection.insert_many(my_list)
                     
    return collection                 
                     


# In[ ]:


def scrape_mars():
    
    # Fresh scrape of all the things...
    print(f"""
    
    -------------------------------------------------
                     Getting News
    -------------------------------------------------""")
    news = mars_news()
    print(f"""
    
    -------------------------------------------------
                     Getting Images
    -------------------------------------------------""")
    featured = mars_image()
    print(f"""
    
    -------------------------------------------------
                     Getting Weather
    -------------------------------------------------""")
    weather = mars_weather()
    print(f"""
    
    -------------------------------------------------
                     Getting Facts
    -------------------------------------------------""")
    facts = mars_facts()
    print(f"""
    
    -------------------------------------------------
                 Getting Hemisphere Info
    -------------------------------------------------""")
    hemi = mars_hemi()
    
    #-------------------
    #  ASSIGN SCRAPED DATA TO VARIABLES
    #-------------------
    mars_pic = last_doc(featured)['image']
    mars_caption = last_doc(featured)['image_desc']
    #-------------------
    news_headline = news.find_one()['title']
    news_teaser = news.find_one()['teaser']
    #-------------------
    mars_today = last_doc(weather)['weather']
    #-------------------
    facts_html = facts[0].find_one()['table_html']
    #-------------------
    hemi_1 = hemi.find()[0]['hemi_image_ref']
    hemi_2 = hemi.find()[1]['hemi_image_ref']
    hemi_3 = hemi.find()[2]['hemi_image_ref']
    hemi_4 = hemi.find()[3]['hemi_image_ref']
    #-------------------
    facts[0].find_one()['table_html']
    
    
    #-------------------
    #  CREATE POST FOR MONGO
    #-------------------
    post = {
        'timestamp':ts()[0],
        'date':ts()[1],
        'featured':mars_pic,
        'caption':mars_caption,
        'news_headline':news_headline,
        'news_body':news_teaser,
        'weather':mars_today,
        'facts':facts_html,        
        'hemi_1':hemi_1,
        'hemi_2':hemi_2,
        'hemi_3':hemi_3,
        'hemi_4':hemi_4,
    }
    
    
    #-------------------
    #  LOAD POST IN MONGO
    #-------------------
    my_db = 'mission_to_mars'
    my_col = 'mars_scrape'
    collection = mongo_me(my_db,my_col)
    collection.insert_one(post)
    doc_count = collection.estimated_document_count()
    
    print(f"""
    
    -------------------------------------------------
    New Mars Record Scraped and Posted on {ts()[1]}
    -------------------------------------------------
       Your Collection has {doc_count} Document(s)
    -------------------------------------------------
    
    """)
    
    return collection
    



#mars = scrape_mars()

