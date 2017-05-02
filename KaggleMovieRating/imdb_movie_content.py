import requests
import json
from bs4 import BeautifulSoup
import time
import random
import re
import datetime

def parse_facebook_likes_number(num_likes_string):
    if num_likes_string[-1] == 'K':
        thousand = 1000
    else:
        thousand = 1
    return float(num_likes_string.replace('K','')) * thousand

def parse_duration(time_string):
    time_string = time_string.split('min')[0]
    x = time.strptime(time_string,'%Hh%M')
    return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

class ImdbMovieContent():
  def __init__(self, movies):
    self.movies = movies
    self.base_url = "http://www.imdb.com"

  def get_facebook_likes(self, entity_id):
    if entity_id.startswith('nm'):
        url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Fname%2F{}%2F&colorscheme=light".format(entity_id)
    elif entity_id.startswith('tt'):
        url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Ftitle%2F{}%2F&colorscheme=light".format(entity_id)
    else:
        url = None
    time.sleep(random.uniform(0, 0.25)) # randomly snooze a time within [0, 0.4] second
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        sentence = soup.find_all(id="u_0_2")[0].span.string # get sentence like: "43K people like this"
        num_likes = sentence.split(" ")[0]
    except Exception as e:
        num_likes = None
    return parse_facebook_likes_number(num_likes)

  def get_id_from_url(self, url):
    if url is None:
        return None
    return url.split('/')[4]

  def parse(self):
    movies_content = []
    for movie in self.movies:
      imdb_url = movie['imdb_url']
      response = requests.get(imdb_url)
      bs = BeautifulSoup(response.text, 'lxml')
      movies_content.append(self.get_content(bs))
    return movies_content

  def get_awards(self, movie_link):
    awards_url = movie_link + 'awards'
    response = requests.get(awards_url)
    bs = BeautifulSoup(response.text, 'lxml')
    awards = bs.find_all('tr')
    award_dict = []
    for award in awards:
        if 'rowspan' in award.find('td').attrs:
            rowspan = int(award.find('td')['rowspan'])
            if rowspan == 1:
                award_dict.append({'category' : award.find('span', class_='award_category').text, 
                                   'type' : award.find('b').text,
                                   'award': award.find('td', class_='award_description').text.split('\n')[1].replace('            ', '')})
            else:
                index = awards.index(award)
                dictt = {'category':award.find('span', class_='award_category').text, 
                         'type' : award.find('b').text}
                awards_ = []
                for elem in awards[index:index+rowspan]:
                    award_dict.append({'category':award.find('span', class_='award_category').text, 
                                         'type' : award.find('b').text,
                                        'award': elem.find('td', class_='award_description').text.split('\n')[1].replace('            ', '')})
    award_nominated = [{k:v for k,v in award.items() if k != 'type'} for award in award_dict if award['type'] == 'Nominated']
    award_won = [{k:v for k,v in award.items() if k != 'type'} for award in award_dict if award['type'] == 'Won']
    return award_nominated, award_won

  def get_content(self, bs):
    movie = {}
    try:
        title_year = bs.find('div', class_ = 'title_wrapper').find('h1').text.encode('latin').decode('utf-8', 'ignore').replace(') ','').split('(')
        movie['movie_title'] = title_year[0]
    except:
        movie['movie_title'] = None
    try:
        movie['title_year'] = title_year[1]
    except:
        movie['title_year'] = None
    # try:
    #     movie['genres'] = '|'.join([genre.text.replace(' ','') for genre in bs.find('div', {'itemprop': 'genre'}).find_all('a')])
    # except:
    #     movie['genres'] = None
    try:
        title_details = bs.find('div', {'id':'titleDetails'})
        movie['language'] = '|'.join([language.text for language in title_details.find_all('a', href=re.compile('language'))])
        movie['country'] = '|'.join([country.text for country in title_details.find_all('a', href=re.compile('country'))])
    except:
        movie['language'] = None
    try:
        keywords = bs.find_all('span', {'itemprop':'keywords'})
        movie['keywords'] = '|'.join([key.text for key in keywords])
    except:
        movie['keywords'] = None
    try:
        movie['storyline'] = bs.find('div', {'id':'titleStoryLine'}).find('div', {'itemprop':'description'}).text.replace('\n', '')
    except:
        movie['storyline'] = None
    try:
        movie['contentRating'] = bs.find('span', {'itemprop':'contentRating'}).text.split(' ')[1]
    except:
        movie['contentRating'] = None
    try:
        movie['color'] = bs.find('a', href=re.compile('colors')).text
    except:
        movie['color'] = None
    try:
        movie['idmb_score'] = bs.find('span', {'itemprop':'ratingValue'}).text
    except:
        movie['idmb_score'] = None
    try:
        movie['num_voted_users'] = bs.find('span', {'itemprop':'ratingCount'}).text.replace(',',)
    except:
        movie['num_voted_users'] = None
    try:
        movie['duration_sec'] = parse_duration(bs.find('time', {'itemprop':'duration'}).text.replace(' ','').replace('\n', ''))
    except:
        movie['duration_sec'] = None
    try:
        review_counts = [int(count.text.split(' ')[0].replace(',', '')) for count in bs.find_all('span', {'itemprop':'reviewCount'})]
        movie['num_user_for_reviews'] = review_counts[0]
    except:
        movie['num_user_for_reviews'] = None
    try:
        prod_co = bs.find_all('span', {'itemtype': re.compile('Organization')})
        movie['production_co'] = [elem.text.replace('\n','') for elem in prod_co]
    except:
        movie['production_co'] = None
    try:
        movie['num_critic_for_reviews'] = review_counts[1]
    except:
        movie['num_critic_for_reviews'] = None
    try:
        actors = bs.find('table', {'class':'cast_list'}).find_all('a', {'itemprop':'url'})
        pairs_for_rows = [(self.base_url + actor['href'], actor.text.replace('\n', '')[1:]) for actor in actors]
        movie['cast_info'] = [{'actor_name' : actor[1], 
                           'actor_link' : actor[0], 
                           'actor_fb_likes': self.get_facebook_likes(self.get_id_from_url(actor[0]))} for actor in pairs_for_rows]
    except:
        movie['cast_info'] = None
    try:
        director = bs.find('span', {'itemprop':'director'}).find('a')
        director = (self.base_url + director['href'].replace('?','/?'), director.text)
        movie['director_info'] = {'director_name':director[1],
                              'director_link':director[0],
                              'director_fb_links': self.get_facebook_likes(self.get_id_from_url(director[0]))}
    except:
        movie['director_info'] = None
    try:
        movie['movie_imdb_link'] = bs.find('link')['href']
        movie['num_facebook_like'] = self.get_facebook_likes(self.get_id_from_url(movie['movie_imdb_link']))
    except:
        movie['num_facebook_like'] = None
    try:
        poster_image_url = bs.find('div', {'class':'poster'}).find('img')['src']
        movie['image_urls'] = poster_image_url.split("_V1_")[0] + "_V1_.jpg"
    except:
        movie['image_urls'] = None
    try:
        award_nominated, award_won = self.get_awards(movie['movie_imdb_link'])
        movie['awards'] = {"won": award_won, 'nominated': award_nominated}
    except Exception as e:
        print(e)
        movie['awards'] = None
    return movie


