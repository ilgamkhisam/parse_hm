import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from datetime import datetime
from models import PostManager
import re

def get_html(url):
    '''Для получения html страницы'''
    r = requests.get(url)
    html = r.text
    html = BeautifulSoup(html, 'html.parser')
    return html

def get_last_page():
    '''Получаем номер последней страницы'''
    URL = 'https://www.bazar.kg/kyrgyzstan/elektronika/kompyutery/noutbuki'
    html = get_html(URL)
    flash_container = html.find('div', {'class':'content-wrapper padding-top-0'})
    all_ul = flash_container.find('ul', {'class':'pagination'})
    last_page = all_ul.find_all('li', {'class': 'page-item'})[-2].text.strip()
    return int('2')

    
def get_links_all_posts(link):
    '''Получаем ссылки всех постов'''
    post_links = []
    link = get_html(link)
    main_content = link.find('div', {'class':'main-content'})
    new_rows = main_content.find_all('div', {'class': 'listing row-5'})
    
    for post in new_rows: 
        post_link = post.find('p', {'class': 'title'}).find_next().get('href').strip()
        post_link = "https://www.bazar.kg" + post_link
        post_links.append(post_link)

    return post_links

def get_data(page):
    '''Собираем детальную информацию из каждого поста'''
    page_html = get_html(page)
    main_div = page_html.find('div', class_='content-wrapper padding-top-0')
    left_side = main_div.find('div', class_='left')
    details_info = left_side.find('div', class_='details-info')
    # блок с информацией
    title = re.sub(r'[ЁёА-я]', '', left_side.find('h1').text.strip()) # регулярные функция для того что бы убрать символы кирилицы из названия продукта 
    description = details_info.find('p', class_='description').text.strip()
    try: 
        price_som = details_info.find('span', class_='main').text.strip().split(' ')[0]
        price_dollar = details_info.find('span', class_='sub').text.strip().split(' ')[1]
    except AttributeError: 
        price_som = '0'
        price_dollar = '0'

    info = {
        'title': title,
        'description': description, 
        'price_som': price_som, 
        'price_dollar': price_dollar,
        'link': page
    }
    return info

def write_db(info): 
    manager = PostManager()
    manager.insert_data(info)

def go_little_rockstar(i):
    URL = 'https://www.bazar.kg/kyrgyzstan/elektronika/kompyutery/noutbuki?page=1'
    URL += f'&page={i}'
    
    manager = PostManager()
    link = get_html(URL)
    main_content = link.find('div', {'class':'main-content'})
    new_rows = main_content.find_all('div', {'class': 'listing row-5'})
    
    for post in new_rows: 
        post_link = post.find('p', {'class': 'title'}).find_next().get('href').strip()
        post_link = "https://www.bazar.kg" + post_link
        data=get_data(post_link)
        if not manager.check_link(data['link']):
            write_db(data)

def main():

    with Pool(40) as pool:
        pool.map(go_little_rockstar, range(1,get_last_page()+1))
        

if __name__ == '__main__':
    start = datetime.now()
    from utils import create_tables
    create_tables()
    main()
    end = datetime.now()
    print(end - start)
