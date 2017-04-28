from bs4 import BeautifulSoup
import json
import requests
import urllib
from imdb_movie_content import ImdbMovieContent
from tqdm import tqdm
import locale
import pandas as pd
import re
import sys

def parse_price(price):
    if not price:
        return 0
    price = price.replace(',', '')
    return locale.atoi(re.sub('[^0-9,]', "", price))

def get_movie_budget():
    movie_budget_url = 'http://www.the-numbers.com/movie/budgets/all'
    response = requests.get(movie_budget_url)
    bs = BeautifulSoup(response.text, 'lxml')
    table = bs.find('table')
    rows = [elem for elem in table.find_all('tr') if elem.get_text() != '\n']
    
    movie_budget = []
    for row in rows[1:]:
        specs = [elem.get_text() for elem in row.find_all('td')]
        movie_name = specs[2].encode('latin1').decode('utf8', 'ignore')
        movie_budget.append({'release_date': specs[1],
                                  'movie_name': movie_name,
                                  'production_budget': parse_price(specs[3]),
                                  'domestic_gross': parse_price(specs[4]),
                                  'worldwide_gross': parse_price(specs[5])})
    
    return movie_budget

def get_imdb_urls(movie_budget, nb_elements=None):
    for movie in tqdm(movie_budget[:nb_elements]):
        movie_name = movie['movie_name']
        title_url = urllib.parse.quote(movie_name.encode('utf-8'))
        imdb_search_link = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(title_url)
        response = requests.get(imdb_search_link)
        bs = BeautifulSoup(response.text, 'lxml')
        results = bs.find("table", class_= "findList" )
        try:
            movie['imdb_url'] = "http://www.imdb.com" + results.find('td', class_='result_text').find('a')['href']
        except:
            movie['imdb_url'] = None
    
    with open('movie_budget.json', 'w') as fp:
        json.dump(movie_budget, fp)

def get_imdb_content(movie_budget_path, nb_elements=None):
    with open(movie_budget_path, 'r') as fp:
        movies = json.load(fp)
    content_provider = ImdbMovieContent(movies)
    contents = []
    for i, movie in tqdm(enumerate(movies[:nb_elements])):
        imdb_url = movie['imdb_url']
        response = requests.get(imdb_url)
        bs = BeautifulSoup(response.text, 'lxml')
        movies_content = content_provider.get_content(bs)
        contents.append(movies_content)
        if i == 100:
            with open('movie_contents.json', 'w') as fp:
                json.dump(contents, fp)    
    
    with open('movie_contents.json', 'w') as fp:
        json.dump(contents, fp)    

def parse_awards(movie):
    awards_kept = ['Oscar', 'BAFTA Film Award', 'Golden Globe', 'Palme d\'Or']
    awards_category = ['won', 'nominated']
    parsed_awards = {}
    for category in awards_category:
        for awards_type in awards_kept:
            awards_cat = [award for award in movie['awards'][category] if award['category'] == awards_type]
            for k, award in enumerate(awards_cat):
                parsed_awards['{}_{}_{}'.format(awards_type, category, k+1)] = award["award"]
    return parsed_awards

def parse_actors(movie):
    sorted_actors = sorted(movie['cast_info'], key=lambda x:x['actor_fb_likes'], reverse=True)
    top_k = 3
    parsed_actors = {}
    parsed_actors['total_cast_fb_likes'] = sum([actor['actor_fb_likes'] for actor in movie['cast_info']]) + movie['director_info']['director_fb_links']
    for k, actor in enumerate(sorted_actors[:top_k]):
        if k < len(sorted_actors):
            parsed_actors['actor_{}_name'.format(k+1)] = actor['actor_name']
            parsed_actors['actor_{}_fb_likes'.format(k+1)] = actor['actor_fb_likes']
        else:
            parsed_actors['actor_{}_name'.format(k+1)] = None
            parsed_actors['actor_{}_fb_likes'.format(k+1)] = None
    return parsed_actors

def create_dataframe(movies_content_path, movie_budget_path):
    with open(movies_content_path, 'r') as fp:
        movies = json.load(fp)
    with open(movie_budget_path, 'r') as fp:
        movies_budget = json.load(fp)
    movies_list = []
    for movie in movies:
        content = {k:v for k,v in movie.items() if k not in ['awards', 'cast_info', 'director_info']}
        name = movie['movie_title']
        try:
            budget = [film for film in movies_budget if film['movie_name']==name][0]
            budget = {k:v for k,v in budget.items() if k not in ['imdb_url', 'movie_name']}
            content.update(budget)
        except: 
            pass
        try:
            content.update(parse_awards(movie))
        except:
            pass
        try:
            content.update({k:v for k,v in movie['director_info'].items() if k!= 'director_link'})
        except:
            pass
        try:
            content.update(parse_actors(movie))
        except:
            pass
        movies_list.append(content)
    df = pd.DataFrame(movies_list)
    df = df[pd.notnull(df.idmb_score)]
    return df

if __name__ == '__main__':
    if len(sys.argv) > 1:
        nb_elements = int(sys.argv[1])
    else:
        nb_elements = None
    movie_budget = get_movie_budget()
    movies = get_imdb_urls(movie_budget, nb_elements=nb_elements)
    get_imdb_content("movie_budget.json", nb_elements=nb_elements)


