import requests
from bs4 import BeautifulSoup
import json
def list_kyiv_bud(id):
    try:
        url = f'https://api.yasno.com.ua/api/v1/electricity-outages-schedule/houses?region=kiev&street_id={id}'
        responce = requests.get(url).text
        data = json.loads(responce)
        list = []
        for i in data:
            list.append(i['name'])
        return list
    except Exception:
        return "Нема нічо"

def get_id(url):
    try:
        if url:
            responce = requests.get(url).text
            data = json.loads(responce)
            return data[0]['street_id']
    except Exception:
        return False

def kyiv_done(url):
    try:
        if url:
            responce = requests.get(url).text
            data = json.loads(responce)
            return (f"черга - {data[0]['group']}\n")
    except Exception:
        return False

# Функція шукає чергу
def check_kyiv(vul):
        with open('s.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            for vuls in data:
                if vuls['name'].capitalize() == vul.capitalize():
                    return vuls['id']
                else:
                    continue
def check(url):
    try:
        responce = requests.get(f'{url}')
        page = responce.text
        soup = BeautifulSoup(page, 'html.parser')
        done = soup.find('div', class_='channel_notice').find('b').text
        return done
    except Exception:
        return "Введіть ще раз!"


# Функція 'чи співпадає написана вулиця з реєстром вулиць'
def check_misto_vul(url, misto):
    list_ = []
    responce = requests.get(f'{url}')
    page = responce.text
    soup = BeautifulSoup(page, 'html.parser')
    done = soup.find('ul', class_='cities_list')
    for vul in done.find_all('a'):
        list_.append(vul.text.title())
    if misto.title() in list_:
        return True
    else:
        return False
