import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from utils import create_tables
from models import PostManager
import re 



async def get_html(url):
    '''Для получения html страницы / Был применено ассихронный код, чтобы не ждать ответа от сервера'''
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            html = BeautifulSoup(html, 'html.parser')
            return html


def get_last_page(html):
    '''Получаем номер последней страницы'''
    flash_container = html.find('div', {'class':'content-wrapper padding-top-0'})
    all_ul = flash_container.find('ul', {'class':'pagination'})
    last_page = all_ul.find_all('li', {'class': 'page-item'})[-2].text.strip()
    return int('10')

def get_all_pages(html):
    '''Получаем список ссылок всех страниц'''
    URL = 'https://www.bazar.kg/kyrgyzstan/elektronika/kompyutery/noutbuki?page=1'
    lp = get_last_page(html)
    links = []
    for i in range(1, lp+1):
        URL += f'&page={i}'
        links.append(URL)

    return links

async def get_links_all_posts(link):
    '''Получаем ссылки всех постов'''
    post_links = []
    html = await get_html(link)
    main_content = html.find('div', {'class':'main-content'})
    new_rows = main_content.find_all('div', {'class': 'listing row-5'})

    for post in new_rows: 
        post_link = post.find('p', {'class': 'title'}).find_next().get('href').strip()
        post_link = "https://www.bazar.kg" +  post_link
        post_links.append(post_link)

    return post_links

async def get_data(posts_links):
    '''Собираем детальную информацию из каждого поста'''
    data = []
    for page in posts_links: 
        page_html = await get_html(page)
        main_div = page_html.find('div', class_ ='content-wrapper padding-top-0')
        left_side = main_div.find('div', class_ = 'left')
        details_info = left_side.find('div', class_ = 'details-info')
        # блок с информацией
        title = re.sub(r'[ЁёА-я]', '', left_side.find('h1').text.strip()) # регулярные функция для того что бы убрать символы кирилицы из названия продукта 
        description = details_info.find('p', class_ = 'description').text.strip()
        try: 
            price_som = details_info.find('span', class_ = 'main').text.strip().split(' ')[0]
            price_dollar = details_info.find('span', class_ = 'sub').text.strip().split(' ')[1]
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
        data.append(info)
    return data

def write_db(info): 
    manager = PostManager()
    manager.insert_data(info)

async def main():
    URL = 'https://www.bazar.kg/kyrgyzstan/elektronika/kompyutery/noutbuki'
    manager = PostManager()
    html = await get_html(URL)
    links = get_all_pages(html)

    for link in links: 
        data = await get_data(await get_links_all_posts(link))
        for i in data:
            if not manager.check_link(i['link']):
                write_db(i)

if __name__ == '__main__':
    start = datetime.now()
    create_tables()
    asyncio.run(main())
    end = datetime.now()
    print(end - start)
