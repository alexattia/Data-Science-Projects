from selenium import webdriver
import urllib
import time
import numpy as np
import glob
import os
import datetime
from bs4 import BeautifulSoup
import smtplib
import config

C = config.Config()

driver = webdriver.Chrome()
driver.set_page_load_timeout(15)

query = '#machinelearningflashcards'
driver.get("https://twitter.com/search?f=tweets&vertical=default&q={}".format(urllib.parse.quote(query)))

length = []
while True:
    time.sleep(np.random.randint(50,100)*0.01)
    tweets_found = driver.find_elements_by_class_name('tweet') 
    driver.execute_script("return arguments[0].scrollIntoView();", tweets_found[::-1][0])
    
    # Stop the loop while no more found tweets 
    length.append(len(tweets_found))
    if len(tweets_found) > 200 and (len(length) - len(set(length))) > 2:
        break

tweets = []
for tweet in tweets_found:
    tweet_dict = {}
    tweet = tweet.get_attribute('innerHTML')
    bs = BeautifulSoup(tweet.strip(), "lxml")
    tweet_dict['username'] = bs.find('span', class_='username').text
    timestamp = float(bs.find('span', class_='_timestamp')['data-time'])
    tweet_dict['date'] = datetime.datetime.fromtimestamp(timestamp)
    tweet_dict['text'] = bs.find('p', class_='tweet-text').text
    try:
        tweet_dict['images'] = [k['src'] for k in bs.find('div', class_="AdaptiveMedia-container").find_all('img')]
    except:
        tweet_dict['images'] = []
    if len(tweet_dict['images']) > 0:
        tweet_dict['text'] = tweet_dict['text'][:tweet_dict['text'].index('pic.twitter')-1]
    tweets.append(tweet_dict)
driver.close()

# We keep only tweets by chrisalbon with pictures
search_tweets = [tw for tw in tweets if tw['username'] == '@chrisalbon' and len(tw['images']) > 0]
# He made multiple tweets on the same topic, we keep only the most recent tweets
# We use the indexes of the reversed tweet list and dictionnaries to keep only key 
unique_search_index = sorted(list({t['text'].lower():i for i,t in list(enumerate(search_tweets))[::-1]}.values()))
unique_search_tweets = [search_tweets[i] for i in unique_search_index]

# Keep non-downloaded tweets
most_recent_file = sorted([datetime.datetime.fromtimestamp(os.path.getmtime(path)) 
                           for path in glob.glob("./downloaded_pics/*.jpg")], reverse=True)[0]
recent_seach_tweets = [tw for tw in unique_search_tweets if tw['date'] > most_recent_file]

# Downloading pictures
for tw in recent_seach_tweets:
    img_url = tw['images'][0]
    filename = tw['text'][:tw['text'].index("#")-1].lower().replace(' ','_')
    filename = "./downloaded_pics/%s.jpg" % filename
    urllib.request.urlretrieve(img_url, filename)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(C.my_email_address, C.password)
 
C.msg.format()
server.sendmail(C.my_email_address, C.dest, msg)
server.quit()
