import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

def convert_formation(s):
    mapping = {'IEP' : ['Institut d\'études politiques', 'IEP'],
     'ENA' : ['ENA', 'École nationale d\'administration'],
     'ENS': ['École normale supérieure', 'ENS'],
     'ENPC':['École nationale des ponts et chaussées', 'ENPC'],
     'X': ['École polytechnique'],
     'HEC': ['HEC', 'École des hautes études commerciales'],
     'ESCP': ['ESCP', 'École supérieure de commerce de Paris'],
     'ESSEC' : ['ESSEC', "École Supérieure des Sciences Economiques et Commerciales "]
    }
    etudes = []
    for key, value in mapping.items():
        for v in value:
            if v in s:
                etudes.append(key)
                break
    return etudes

def get_ministres(link):
    browser = webdriver.Chrome()
    try:
        browser.get(link)
        time.sleep(0.2)
    except:
        time.sleep(1)
    text = browser.find_element_by_xpath('//div[@id="mw-content-text"]').get_attribute('innerHTML').strip()
    bs = BeautifulSoup(text, 'lxml')
    ministres_l = [[(k.text.replace('\u200d ','') , k.find('a')['href']) for k in e.find_parents()[1].find_all('td') if k.text !='' and k.find('a')] 
                   for e in bs.find_all('a', class_="image")]
    ministres = [{'Poste':k[0][0], 'Nom':k[::-1][1][0], 'Lien':'https://fr.wikipedia.org' + k[::-1][1][1]} for k in ministres_l if len(k) > 1][:-1]
    for m in ministres:
        m['Formation'] = get_formation(m['Lien'])
    browser.quit()
    return ministres

def get_formation(link_bio):
    browser = webdriver.Chrome()
    browser.set_page_load_timeout(15)
    try:
        browser.get(link_bio)
    except:
        time.sleep(1.5)
    bs = BeautifulSoup(browser.find_element_by_xpath('//div[@id="mw-content-text"]').get_attribute('innerHTML').strip(), 'lxml')
    try:
        h3_elem = [e.find('span').text for e in bs.find_all('h3')]
        h3_elem_formation = [k for k in h3_elem if 'formation' in k.lower() or 'études' in k.lower() or 'etudes' in k.lower() or 'parcours' in k.lower() 
                                                                            or "cursus" in k.lower()][0]
        f, s = h3_elem[h3_elem.index(h3_elem_formation):h3_elem.index(h3_elem_formation)+2]
    except:
        h2_elem = [e.find('span').text for e in bs.find_all('h2')[1:]]
        h2_elem_biographie = [k for k in h2_elem if 'biographie' in k.lower() or 'carrière' in k.lower() or 'formation' in k.lower() or 'parcours' in k.lower()
                                                     or "cursus" in k.lower()][0]
        f, s = h2_elem[h2_elem.index(h2_elem_biographie):h2_elem.index(h2_elem_biographie)+2]
    try:
        first, second = [m.start() for m in re.finditer(f, bs.text)][1], [m.start() for m in re.finditer(s, bs.text)][1]
        browser.quit()
        s = bs.text[first:second].replace('\n', '')
        return convert_formation(re.sub(r'\[*\d*\]', '', s))
    except:
        print('Error for %s' % link_bio)

def get_previous_government_link(browser, link):
    try:
        browser.get(link)
        time.sleep(0.5)
    except:
        time.sleep(1.5)
    box = browser.find_element_by_xpath('//table[@class="infobox_v2"]')
    browser.execute_script("return arguments[0].scrollIntoView();", box)
    bs = BeautifulSoup(box.get_attribute('innerHTML').strip(), 'lxml')
    d = dict(set([([k.replace('|','').replace('\n','') for k in e.text.replace('\n\n','|').split('||') if k != ''][0], 
                 "https://fr.wikipedia.org" + e.find('a')['href']) 
                for e in bs.find_all('tr') if e.find('img', {'alt':"Précédent"})]))
    duration = [e.find('td').text.encode().decode('ascii', 'ignore') for e in bs.find_all('tr') if e.find('th', text='Durée')][0]
    return d, duration


def convert_duration(dur):
    splits = [''.join([s for s in elem if s.isdigit()]) for elem in dur.split('an')]
    if len(splits) == 2:
        return 365 * int(splits[0]) + int(splits[1])
    else:
        return int(splits[0])