import requests
from bs4 import BeautifulSoup
import json
from pdf2image import convert_from_path


# str_json = """[{"id":1,"name":"1\u0439 \u043f\u0440\u043e\u0432\u0443\u043b\u043e\u043a \u0422\u0443\u043f\u0438\u043a\u043e\u0432\u0438\u0439(\u0411\u043e\u0440\u0442\u043d\u0438\u0447\u0456)"},{"id":2,"name":"2-\u0438\u0439 \u043f\u0440\u043e\u0432\u0443\u043b\u043e\u043a \u041b\u0456\u0441\u043e\u0441\u0442\u0435\u043f\u043e\u0432\u0438\u0439"}]"""

url = f'https://api.yasno.com.ua/api/v1/electricity-outages-schedule/houses?region=kiev&street_id={7}'

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
            return (data[0]['group'])
    except Exception:
        return False


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


def checck(vul):
    with open('s.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        l = []
        k = []
        for i in data:
            if vul in i['name']:

                l.append(i)

            else:
                print(i)
                continue
        for i in l:
            k.append(i['name'])

        return k


def dowload_pdf(url='', num=''):

    try:
        responce = requests.get(url=url)
        with open(f'grafik_group{num}.pdf', 'wb') as file:
            file.write(responce.content)

        return 'Img succ'
    except Exception as ex:
        return 'Upps'


def page_to_img(num):
    pages = convert_from_path(f'grafik_group{num}.pdf', poppler_path=r'poppler-23.11.0\Library\bin')


    for i, page in enumerate(pages):
        page.save(f'grafik_{i}_num.jpg', 'JPEG')

