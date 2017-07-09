#!/usr/bin/env python
from selenium import webdriver
import urllib
import time
import sys
import numpy as np
import glob
import os
import datetime
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import config

def internet_on():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError: 
        return False

def get_all_tweets(query):
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.set_page_load_timeout(20)
    driver.get("https://twitter.com/search?f=tweets&vertical=default&q={}".format(urllib.parse.quote(query)))

    length = []
    while True:
        time.sleep(np.random.randint(50,100)*0.01)
        tweets_found = driver.find_elements_by_class_name('tweet') 
        driver.execute_script("return arguments[0].scrollIntoView();", tweets_found[::-1][0])
        
        # Stop the loop while no more found tweets 
        length.append(len(tweets_found))
        if len(tweets_found) > 200 and (len(length) - len(set(length))) > 2:
            print('%s tweets found at %s' % (len(tweets_found), datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')))
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
    return tweets

def filter_tweets(tweets):
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
    recent_seach_tweets = [tw for tw in unique_search_tweets if tw['date'] > datetime.datetime(2017, 7, 6, 16, 42, 56)]
    return recent_seach_tweets

def download_pictures(recent_seach_tweets):
    # Downloading pictures
    print('Downloading %d tweets' % len(recent_seach_tweets))
    for tw in recent_seach_tweets:
        img_url = tw['images'][0]
        filename = tw['text'][:tw['text'].index("#")-1].lower().replace(' ','_')
        filename = "./downloaded_pics/%s.jpg" % filename
        urllib.request.urlretrieve(img_url, filename)

def send_email(recent_seach_tweets):
    # Create e-mail message
    msg = C.intro + C.message_init.format(number_flash_cards=len(recent_seach_tweets)) 
    for tw in recent_seach_tweets[:3]:
        date = tw['date'].strftime('Le %d/%m/%Y à %H:%M')
        link_picture = tw['images'][0]
        tweet_text = tw["text"][:tw["text"].index('#')-1]
        msg += C.flashcard.format(date=date, link_picture=link_picture, tweet_text=tweet_text)

    numbers = { 0 : 'zero', 1 : 'one', 2 : 'two', 3 : 'three', 4 : 'four', 5 : 'five',
              6 : 'six', 7 : 'seven', 8 : 'eight', 9 : 'nine', 10 : 'ten'}

    message = MIMEText(msg, 'html')
    message['From'] = formataddr((str(Header('Twitter Parser', 'utf-8')), C.my_email_address))
    message['To'] = C.dest
    message['Subject'] = '%s new Machine Learning Flash Cards' % numbers[len(recent_seach_tweets)].title()
    msg_full = message.as_string()

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(C.my_email_address, C.password)
    server.sendmail(C.my_email_address, C.dest, msg_full)
    server.quit()
    print('E-mail sent!')

if __name__ == '__main__':
    C = config.Config()
    query = '#machinelearningflashcards'
    time_slept = 0
    while not internet_on():
        time.sleep(1)
        time_slept += 1
        if time_slept > 15 : 
            print('%s - No network connection' % datetime.datetime.now().strftime('%d/%m/%Y - %H:%M'))
            sys.exit()
    tweets = get_all_tweets(query)
    recent_seach_tweets = filter_tweets(tweets)
    if len(recent_seach_tweets) > 0:
        download_pictures(recent_seach_tweets)
        send_email(recent_seach_tweets)
    else:
        print('No picture to download')
    print('\n')


