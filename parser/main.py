from bs4 import BeautifulSoup as bs4
from openpyxl import Workbook
import requests

BASE_URL = 'https://cataz.net/'
GENRE_URL = 'genre/horror'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
}


def get_html():
    r = requests.get(BASE_URL + GENRE_URL, headers=headers)
    return r


def get_total_page_num(html):
    soup = bs4(html.text, 'html.parser')
    return int(soup.find('a', title='Last')['href'].split('=')[-1])


def get_all_movies_ulrs(pages_num):
    urls = []
    for i in range(1, pages_num + 1):
        if i == 1:
            r = requests.get(BASE_URL + GENRE_URL, headers=headers)
        else:
            params = {
                'page': i,
            }
            r = requests.get(BASE_URL + GENRE_URL, headers=headers, params=params)
        soup = bs4(r.text, 'html.parser')
        movies_urls = soup.find_all('a', {'class': 'film-poster-ahref flw-item-tip'})
        for data in movies_urls:
            urls.append(data['href'])
        print(f'Page {i} done.')
    return urls

def get_movie_data(route):
    r = requests.get(BASE_URL + route, headers=headers)
    soup = bs4(r.text, 'html.parser')
    name = soup.find('h2', class_='heading-name').a.contents[0]
    imdb = soup.find('span', class_='item mr-2').button.contents[0].split()[-1]
    year = soup.find('div', class_='col-xl-5 col-lg-6 col-md-8 col-sm-12').find_all('div', class_='row-line')[0].contents[2][1:5]
    genre = soup.find('div', class_='col-xl-5 col-lg-6 col-md-8 col-sm-12').find_all('div', class_='row-line')[1].find_all('a')
    genre = ' '.join([x['title'] for x in genre])
    duraction = soup.find('div', class_='col-xl-6 col-lg-6 col-md-4 col-sm-12').find_all('div', class_='row-line')[0].contents[2].split()
    duraction = duraction[0] + ' ' + duraction[1]
    country = soup.find('div', class_='col-xl-6 col-lg-6 col-md-4 col-sm-12').find_all('div', class_='row-line')[1].find_all('a')
    country = ' '.join([x['title'] for x in country])
    return (name, imdb, year, genre, duraction, country, BASE_URL + route)

def write_in_excel(data):
    wb = Workbook()
    ws = wb.active
    ws.title = GENRE_URL.split('/')[-1]
    ws.append(('name', 'IMDB', 'year', 'genre', 'duraction', 'country', 'URL'))
    counter = 2
    for item in data:
        ws.append(item)
        counter += 1
    wb.save('movies.xlsx')


if __name__ == '__main__':
    urls = get_all_movies_ulrs(1)
    data = []
    counter = 1
    for url in urls:
        data.append(get_movie_data(url))
        print(f'{counter}-th movie parsed.')
        counter +=1
    write_in_excel(data)
