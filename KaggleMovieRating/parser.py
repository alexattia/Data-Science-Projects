from bs4 import BeautifulSoup
import json
import requests

def get_movie_budget():
    movie_budget_url = 'http://www.the-numbers.com/movie/budgets/all'
    response = requests.get(movie_budget_url)
    bs = BeautifulSoup(response.text, 'lxml')
    table = bs.find('table')
    rows = [elem for elem in table.find_all('tr') if elem.get_text() != '\n']
    
    movie_budget = {'movies':[]}
    for row in rows[1:]:
        specs = [elem.get_text() for elem in row.find_all('td')]
        movie_name = specs[2].encode('latin1').decode('utf8', 'ignore')
        movie_budget['movies'].append({'release_date': specs[1],
                                  'movie_name': movie_name,
                                  'production_budget': specs[3],
                                  'domestic_gross': specs[4],
                                  'worldwide_gross': specs[5]})
    
    with open('movie_budget.json', 'w') as fp:
        json.dump(movie_budget, fp)