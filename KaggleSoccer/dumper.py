import requests
import re
import time
from datetime import datetime
import json
from tqdm import tqdm
import numpy as np
import seaborn as sns
from matplotlib import patches
import pandas as pd
import parser
import sys
import random
from collections import Counter
from bs4 import BeautifulSoup
from sklearn import preprocessing
import urllib

def convert_int(string):
    try:
        string = int(string)
        return string
    except:
        return string

def get_team(request, link=None):
    team = {}
    if not link:
        team_searched = request
        team_searched = urllib.parse.quote(team_searched.encode('utf-8'))
        search_link = "http://us.soccerway.com/search/teams/?q={}".format(team_searched)
        response = requests.get(search_link)
        bs = BeautifulSoup(response.text, 'lxml')
        results = bs.find("ul", class_='search-results')
        # Take the first results
        try:
            link = "http://us.soccerway.com" + results.find_all('a')[0]['href']
            print('Please check team link:', link)
            team['id_'] = results.find_all('a')[0]["href"].split('/')[4]
            team['name'] = results.find_all('a')[0].text
            team['country'] = results.find_all('a')[0]["href"].split('/')[2]
        except:
            print('No team found !')
    else:
        team['id_'] = link.split('/')[6]
        team['name'] = link.split('/')[5]
        team['country'] = link.split('/')[4]
    return team

def get_games(team, nb_pages=12):
    games = []
    for page_number in range(nb_pages):
        link_base = 'http://us.soccerway.com/a/block_team_matches?block_id=page_team_1_block_team_matches_3&callback_params=' 
        link_ = urllib.parse.quote('{"page":0,"bookmaker_urls":[],"block_service_id":"team_matches_block_teammatches","team_id":%s,\
        "competition_id":0,"filter":"all","new_design":false}' % team['id_']) + '&action=changePage&params=' + urllib.parse.quote('{"page":-%s}' % (page_number))
        link = link_base + link_
        response = requests.get(link)

        test = json.loads(response.text)['commands'][0]['parameters']['content']
        bs = BeautifulSoup(test, 'lxml')

        for kind in ['even', 'odd']:
            for elem in bs.find_all('tr', class_ = kind):
                game = {}
                game["date"] = elem.find('td', {'class': ["full-date"]}).text
                game["competition"] = elem.find('td', {'class': ["competition"]}).text
                game["team_a"] = elem.find('td', class_='team-a').text
                game["team_b"] = elem.find('td', class_='team-b').text
                game['link'] = "http://us.soccerway.com" + elem.find('td', class_='score-time').find('a')['href']
                game["score"] = elem.find('td', class_='score-time').text.replace(' ','')
                if 'E' in game["score"]:
                    game["score"] = game['score'].replace('E','')
                    game['extra_time'] = True
                if 'P' in game["score"]:
                    game["score"] = game['score'].replace('P','')
                    game['penalties'] = True
                if datetime.strptime(game["date"], '%d/%m/%y') < datetime.now():
                    game = parser.get_score_details(game, team)
                    time.sleep(random.uniform(0, 0.25))
                    game.update(parser.get_goals(game['link']))
                else:
                    del game['score']
                games.append(game)
        games = sorted(games, key=lambda x:datetime.strptime(x['date'], '%d/%m/%y'))
        team['games'] = games
        return team

def get_squad(team, season_path='./seasons_codes.json'):
    with open(season_path, 'r') as f:
        seasons = json.load(f)[team["country"]]
    
    team['squad'] = {}
    for k,v in seasons.items():
        link_base = 'http://us.soccerway.com/a/block_team_squad?block_id=page_team_1_block_team_squad_3&callback_params='
        link_ = urllib.parse.quote('{"team_id":%s}' % team['id_']) + '&action=changeSquadSeason&params=' + urllib.parse.quote('{"season_id":%s}' % v)
        link = link_base + link_
        response = requests.get(link)
        test = json.loads(response.text)['commands'][0]['parameters']['content']
        bs = BeautifulSoup(test, 'lxml')
        
        players = bs.find('tbody').find_all('tr')
        squad = [{
            k: convert_int(player.find('td', class_=k).text)
              for k in [k for k,v in Counter(np.concatenate([elem.attrs['class'] for elem in player.find_all('td')])).items() 
                        if v < 2 and k not in ['photo', '', 'flag']]
         } for player in players]
        team['squad'][k] = squad
        try:
            coach = {'position': 'Coach', 'name':bs.find_all('tbody')[1].text}
            team['coach'][k] = coach
        except: pass  
    return team 

if __name__ == '__main__':
    if len(sys.argv) > 1:
        request = ' '.join(sys.argv[1:])
    else:
        raise ValueError('You must enter a requested team!')
    team = get_team(request)
    f = input('Satisfied ? (Y/n) ')
    count = 0
    while f not in ['Y', 'y','yes','']:
        if count < 3:
            request = input('Enter a new request : ')
            link = None
        else:
            link = input('Paste team link : ')
        team = get_team(request, link)
        f = input('Satisfied ? (Y/n)')
        count += 1
    team = get_games(team)
    team = get_squad(team)
    with open('./teams/%s.json' % team["name"].lower(), 'w') as f:
        json.dump(team, f)
