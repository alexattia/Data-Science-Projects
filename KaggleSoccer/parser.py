import urllib
import requests
import time
import datetime
import json
from tqdm import tqdm
import random
from bs4 import BeautifulSoup

def get_score_details(game, team):
    if game["team_a"] == team['name']:
        game['place'] = 'home'
        game['nb_goals_{}'.format(team['name'])] = int(game['score'].split('-')[0])
        game['nb_goals_adv'] = int(game['score'].split('-')[1])
    else:
        game['place'] = 'away'
        game['nb_goals_{}'.format(team['name'])] = int(game['score'].split('-')[1])
        game['nb_goals_adv'] = int(game['score'].split('-')[0])
    if game['nb_goals_{}'.format(team['name'])] > game['nb_goals_adv']:
        game['result'] = 'WIN'
    elif game['nb_goals_{}'.format(team['name'])] == game['nb_goals_adv']:
        game['result'] = 'TIE'
    else:
        game['result'] = 'LOST'
    return game

def shot_team(row, columns):
    try:
        for col in columns:
            if row['team_a'] == 'PSG':
                row['{}_PSG'.format(col.lower().replace(' ','_'))] = row[col]['team_a'] 
                row['{}_adv'.format(col.lower().replace(' ','_'))] = row[col]['team_b'] 
            else:
                row['{}_PSG'.format(col.lower().replace(' ','_'))] = row[col]['team_b'] 
                row['{}_adv'.format(col.lower().replace(' ','_'))] = row[col]['team_a']
    except:
        pass
    return row

def get_goals_team(bs, team):
    if bs.find('span', class_='bidi').text != ' 0 - 0':
        goals = [{'player':elem.find('a').text, 
                  'time':elem.find('span', class_='minute').text.replace("'",''), 
                  'assist': elem.find('span', class_='assist')} for elem in bs.find('div', class_='block_match_goals').find_all('td', class_='player-{}'.format(team)) if elem.text !='\n\n']
        for goal in goals:
            if goal['assist'] != None:
                goal['assist'] = goal['assist'].text.replace('(assist by ','').replace(')','')
            else:
                del goal['assist']
    else:
        goals=[]
    return goals

def get_lineups(bs):
    lineups = {}
    players = [elem.text.replace('\n','') for elem in bs.find_all('td', class_='large-link')]
    lineups["players_teams_a"] = players[:11]
    lineups["players_team_b"] = players[11:22]
    lineups['subs_in_a'] = [elem[:elem.index('for')] for elem in players[22:29] if 'for' in elem]
    lineups['subs_in_b'] = [elem[:elem.index('for')] for elem in players[29:36] if 'for' in elem]
    return lineups

def get_stats(bs):
    l = bs.find('div', class_='block_match_stats_plus_chart').find('iframe')['src']
    response = requests.get('http://us.soccerway.com/' + l)
    bs2 = BeautifulSoup(response.text,'lxml')
    stats_list = [elem.text[1:-1].split('\n') for elem in bs2.find('table').find('tr').find_all('tr')[1:]][0::2]
    stats = {elem[1]:{'team_a': int(elem[0]), 'team_b':int(elem[2])} for elem in stats_list}
    return stats

def get_goals(link):
    game = {}
    response = requests.get(link)
    bs = BeautifulSoup(response.text, 'lxml')
    try:
        game['goals_a'], game['goals_b'] = [get_goals_team(bs, 'a'), get_goals_team(bs, 'b')]
    except: pass
    try:
        game.update(get_lineups(bs))
    except: pass
    try:
        game.update(get_stats(bs))
    except: pass 
    return game

