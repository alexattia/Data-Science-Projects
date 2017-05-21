from bs4 import BeautifulSoup
import json
import requests
import urllib
from tqdm import tqdm
import locale
import pandas as pd
import re
import time
import random
import sys

from imdb_movie_content import ImdbMovieContent

def parse_price(price):
    """
    Convert string price to numbers
    """
    if not price:
        return 0
    price = price.replace(',', '')
    return locale.atoi(re.sub('[^0-9,]', "", price))

def get_movie_budget():
    """
    Parsing the numbers website to get the budget data.
    :return: list of dictionnaries with budget and gross
    """
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
    """
    Parsing imdb website to get imdb movies links.
    Dumping a json file with budget, gross and imdb urls
    :param movie_budget: list of dictionnaries with budget and gross
    :param nb_elements: number of movies to parse 
    """
    for movie in tqdm(movie_budget[1000:1000+nb_elements]):
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
    """
    Parsing imdb website to get imdb content : awards, casting, description, etc.
    Dumping a json file with imdb content
    :param movie_budget_path: path of the movie_budget.json file
    :param nb_elements: number of movies to parse 
    """
    with open(movie_budget_path, 'r') as fp:
        movies = json.load(fp)
    content_provider = ImdbMovieContent(movies)
    contents = []
    threshold = 1300
    for i, movie in enumerate(movies[threshold:threshold+nb_elements]):
        time.sleep(random.uniform(0, 0.25))
        print("\r%i / %i" % (i, len(movies[threshold:threshold+nb_elements])), end="")
        try:
            imdb_url = movie['imdb_url']
            response = requests.get(imdb_url)
            bs = BeautifulSoup(response.text, 'lxml')
            movies_content = content_provider.get_content(bs)
            contents.append(movies_content)
        except Exception as e:
            print(e)
            pass
    with open('movie_contents7.json', 'w') as fp:
        json.dump(contents, fp)    

def parse_awards(movie):
    """
    Convert awards information to a dictionnary for dataframe.
    Keeping only Oscar, BAFTA, Golden Globe and Palme d'Or awards.
    :param movie: movie dictionnary
    :return: well-formated dictionnary with awards information
    """
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
    """
    Convert casting information to a dictionnary for dataframe.
    Keeping only 3 actors with most facebook likes.
    :param movie: movie dictionnary
    :return: well-formated dictionnary with casting information
    """
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

def parse_production_company(movie):
    """
    Convert production companies to a dictionnary for dataframe.
    Keeping only 3 production companies.
    :param movie: movie dictionnary
    :return: well-formated dictionnary with production companies
    """   
    parsed_production_co = {}
    top_k = 3
    production_companies = movie['production_co'][:top_k]
    for k, company in enumerate(production_companies):
        if k < len(movie['production_co']):
            parsed_production_co['production_co_{}'.format(k+1)] = company
        else:
            parsed_production_co['production_co_{}'.format(k+1)] = None
    return parsed_production_co

def parse_genres(movie):
    """
    Convert genres to a dictionnary for dataframe.
    :param movie: movie dictionnary
    :return: well-formated dictionnary with genres
    """   
    parse_genres = {}
    g = movie['genres']
    with open('genre.json', 'r') as f:
        genres = json.load(f)
    for k, genre in enumerate(g):
        if genre in genres:
            parse_genres['genre_{}'.format(k+1)] = genres[genre]
    return parse_genres

def create_dataframe(movies_content_path, movie_budget_path):
    """
    Create dataframe from movie_budget.json and movie_content.json files.
    :param movies_content_path: path of the movies_content.json file
    :param movie_budget_path: path of the movie_budget.json file
    :return: well formated dataframe
    """
    with open(movies_content_path, 'r') as fp:
        movies = json.load(fp)
    with open(movie_budget_path, 'r') as fp:
        movies_budget = json.load(fp)
    movies_list = []
    for movie in movies:
        content = {k:v for k,v in movie.items() if k not in ['awards', 'cast_info', 'director_info', 'production_co']}
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
            content.update(parse_genres(movie))
        except:
            pass
        try:
            content.update({k:v for k,v in movie['director_info'].items() if k!= 'director_link'})
        except:
            pass
        try:
            content.update(parse_production_company(movie))
        except:
            pass
        try:
            content.update(parse_actors(movie))
        except:
            pass
        movies_list.append(content)
    df = pd.DataFrame(movies_list)
    df = df[pd.notnull(df.idmb_score)]
    df.idmb_score = df.idmb_score.apply(float)
    return df

if __name__ == '__main__':
    if len(sys.argv) > 1:
        nb_elements = int(sys.argv[1])
    else:
        nb_elements = None
    # movie_budget = get_movie_budget()
    # movies = get_imdb_urls(movie_budget, nb_elements=nb_elements)
    get_imdb_content("movie_budget.json", nb_elements=nb_elements)


