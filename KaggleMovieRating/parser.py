from bs4 import BeautifulSoup
import json
import requests
import urllib
from imdb_movie_content import ImdbMovieContent
from tqdm import tqdm

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
                                  'production_budget': specs[3],
                                  'domestic_gross': specs[4],
                                  'worldwide_gross': specs[5]})
    
    return movie_budget

def get_imdb_urls(movie_budget):
    for movie in tqdm(movie_budget):
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
    for movie in movies[:nb_elements]:
        imdb_url = movie['imdb_url']
        response = requests.get(imdb_url)
        bs = BeautifulSoup(response.text, 'lxml')
        movies_content = content_provider.get_content(bs)
        contents.append(movies_content)
    
    with open('movie_contents.json', 'w') as fp:
        json.dump(contents, fp)    
