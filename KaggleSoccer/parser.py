import urllib
import requests
import time
import pandas as pd
import numpy as np
import datetime
import json
from tqdm import tqdm
import random
from bs4 import BeautifulSoup
from collections import Counter

def get_score_details(game, team):
    if game["team_a"] == team['name']:
        game['place'] = 'home'
        try:
            game['nb_goals_{}'.format(team['name'])] = int(game['score'].split('-')[0])
            game['nb_goals_adv'] = int(game['score'].split('-')[1])
        except:pass
    else:
        game['place'] = 'away'
        try:
            game['nb_goals_{}'.format(team['name'])] = int(game['score'].split('-')[1])
            game['nb_goals_adv'] = int(game['score'].split('-')[0])
        except:pass
    try:
        if game['nb_goals_{}'.format(team['name'])] > game['nb_goals_adv']:
            game['result'] = 'WIN'
        elif game['nb_goals_{}'.format(team['name'])] == game['nb_goals_adv']:
            game['result'] = 'TIE'
        else:
            game['result'] = 'LOST'
    except:pass
    return game

def shot_team(row, columns, team_name):
    try:
        for col in columns:
            if row['team_a'] == team_name:
                row['{}_{}'.format(col.lower().replace(' ','_'), team_name.lower())] = row[col]['team_a'] 
                row['{}_adv'.format(col.lower().replace(' ','_'))] = row[col]['team_b'] 
            else:
                row['{}_{}'.format(col.lower().replace(' ','_'), team_name.lower())] = row[col]['team_b'] 
                row['{}_adv'.format(col.lower().replace(' ','_'))] = row[col]['team_a']
    except: pass
    return row

def convert_team_name(row, team_name):
    for col in ['goals', 'players_team', "subs_in"]:
        try:
            if row['team_a'] == team_name:
                row['{}_{}'.format(col, team_name.lower())] = row['{}_a'.format(col)] 
                row['{}_adv'.format(col)] = row['{}_b'.format(col)]  
            else:
                row['{}_{}'.format(col, team_name.lower())] = row['{}_b'.format(col)] 
                row['{}_adv'.format(col)] = row['{}_a'.format(col)]  
            del row['{}_a'.format(col)], row['{}_b'.format(col)] 
        except: pass
    return row    

def player_per_opponent(df, player, team_name):
    stats_player = {}
    for opponent in set(df.opponent):
        try:
            game_played = len([e for e in list(df[df.opponent == opponent]["players_team_%s" % team_name.lower()]) +
                                          list(df[df.opponent == opponent]["subs_in_%s" % team_name.lower()]) 
                             if player in e])
            if game_played > 0:
                goals = len([e for e in np.concatenate([elem for elem in df[df.opponent == opponent]["goals_%s" % team_name.lower()] if type(elem) == list]) 
                                    if e['player'] == player])
                assist = len([e for e in np.concatenate([elem for elem in df[df.opponent == opponent]["goals_%s" % team_name.lower()] if type(elem) == list]) 
                                    if 'assist' in e and e['assist'] == player])
                de = goals + assist

                stats_player[opponent] = {'goals':goals,
                                          'goals_game':goals/game_played,
                                          'decisive_game':de/game_played,
                                         'assists':assist,
                                         'decisive':de,
                                         'games':game_played}
        except: pass
    return stats_player

def ratio_one_opponent(df, opponent, team_name, top_k=10):
    df_oppo = df[df.opponent == opponent]
    game_player = dict(Counter(np.concatenate(list(df_oppo["players_team_%s" % team_name.lower()]) +
                                          list(df_oppo["subs_in_%s" % team_name.lower()]))).items())
    goal_counter = Counter([elem['player'] for elem in np.concatenate(list(df_oppo["goals_%s" % team_name.lower()]))])
    assist_counter = Counter([elem['assist'] for elem in np.concatenate(list(df_oppo["goals_%s" % team_name.lower()])) if "assist" in elem])
    goal_ratio = sorted([(k, v/game_player[k]) for k,v in dict(goal_counter).items() if k in game_player and game_player[k] >= 3 ], 
                        key=lambda x:x[1], reverse=True)[:top_k]
    assist_ratio = sorted([(k, v/game_player[k]) for k,v in dict(assist_counter).items() if k in game_player and game_player[k] >= 3 ], 
                          key=lambda x:x[1], reverse=True)[:top_k]
    decisive_ratio = sorted([(k, v/game_player[k]) for k,v in dict(goal_counter+assist_counter).items() if k in game_player and game_player[k] >= 3 ], 
                            key=lambda x:x[1], reverse=True)[:top_k]
    return goal_ratio, assist_ratio, decisive_ratio

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
    lineups["players_team_a"] = players[:11]
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

def convert_df_games(dict_file):
    df = pd.DataFrame(dict_file["games"])
    df['date'] = pd.to_datetime(df.date.apply(lambda x:'/'.join([x.split('/')[1],x.split('/')[0], x.split('/')[2]])))
    df['month'] = df.date.apply(lambda x:x.month)
    df['year'] = df.date.apply(lambda x:x.year)
    df = df[df.date < datetime.datetime.now()]
    df = df.sort_values('date', ascending=False)
    team_name = df.team_a.value_counts().index[0]
    df['opponent'] = df.apply(lambda x:(x['team_a']+x['team_b']).replace(team_name, ''), axis=1)
    cols = ['Corners', 'Fouls', 'Offsides', 'Shots on target', 'Shots wide']
    df = df.apply(lambda x:shot_team(x, cols, team_name),axis=1)
    df = df.apply(lambda x:convert_team_name(x, team_name),axis=1)
    df = df.drop(cols, axis=1)
    return df
