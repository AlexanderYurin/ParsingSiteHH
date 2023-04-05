import requests
from collections import Counter
from loguru import logger
from bs4 import BeautifulSoup
from time import sleep

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 '
                         'Safari/537.36 '}


def request_to_site(url: str) -> str:
    """
    Фнкция для получение данных по ссылке.
    :param url: ссылка на сайт
    :return: возвращается HTML страница в текстовом виде
     """
    sleep(3)  # чтобы не получить блокировку
    response = requests.get(url, headers=headers)
    return response.text


def number_of_pages(url: str) -> int:
    """
    Функция для получения кол-во страниц на сайте если это необходимо.
    """
    soup = BeautifulSoup(request_to_site(url), 'lxml')
    count = soup.find_all('li', class_='page-item')[-2].text
    return int(count)


def get_article_card(url: str) -> str:
    """Функцкия для генерации уникальной ссылке на вакансию"""
    # for count in range(1, number_of_pages(url) + 1):
    # url_page = f'{url}?page={count}'
    # logger.info(url_page)
    soup = BeautifulSoup(request_to_site(url), 'lxml')
    data = soup.find_all('a', class_='serp-item__title')
    for i_data in data:
        logger.info(i_data)
        url_card = i_data.get('href')
        logger.info(url_card)
        yield url_card


def main() -> None:
    url = r'https://nn.hh.ru/search/vacancy?text=Python&from=suggest_post&area=66'
    all_skills = []
    for site in get_article_card(url):
        soup = BeautifulSoup(request_to_site(site), 'lxml')
        data = soup.find_all('div', class_='bloko-tag bloko-tag_inline')
        skills = [st.find('span').text for st in data]
        all_skills += skills

    for title, count in Counter(all_skills).items():
        with open('info.txt', 'a+', encoding='utf-8') as file:
            file.write(f'{title}:{count}\n')


if __name__ == '__main__':
    main()
