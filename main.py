import requests
from collections import Counter
from bs4 import BeautifulSoup
from time import sleep
from loguru import logger

logger.add("calendar_log.log",
           rotation="10 MB",
           level="INFO",
           format="{time} - {name} - {level} - {message}")

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}


def request_to_site(url: str) -> str:
    """
    Функция для получения данных по ссылке.
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
    # Проверяем, есть ли элемент с классом 'page-item'.
    # Если нет, то возвращаем 1, потому что на сайте только одна страница.
    if not soup.find_all('li', class_='page-item'):
        return 1
    count = soup.find_all('li', class_='page-item')[-2].text
    return int(count)


def get_article_card(url: str) -> str:
    """Функция для генерации уникальной ссылки на вакансию"""
    try:
        for count in range(1, number_of_pages(url) + 1):
            url_page = f'{url}&page={count}'
            soup = BeautifulSoup(request_to_site(url_page), 'lxml')
            data = soup.find_all('a', class_='serp-item__title')
            for i_data in data:
                url_card = i_data.get('href')
                logger.info(f'Полученная ссылка на вакансию {url_card}')
                yield url_card
    except Exception as e:
        # записываем информацию об ошибке в лог-файл
        logger.exception(f'Произошла ошибка в функции get_article_card: {e}')


def main() -> None:
    url = r'https://nn.hh.ru/search/vacancy?text=Python&from=suggest_post&area=66'
    all_skills = []
    for site in get_article_card(url):
        soup = BeautifulSoup(request_to_site(site), 'lxml')
        data = soup.find_all('div', class_='bloko-tag bloko-tag_inline')
        # Создаем список навыков только для текущей вакансии.
        skills = [st.find('span').text for st in data]
        all_skills += skills

    # Используем Counter для подсчета повторений каждого навыка.
    skill_counts = Counter(all_skills)
    with open('info.txt', 'w', encoding='utf-8') as file:
        # Записываем результаты в файл.
        for title, count in sorted(skill_counts.items(), key=lambda x, y: x[y]):
            file.write(f'{title}:{count}\n')
        logger.info('Файл успешно создан!')

if __name__ == '__main__':
    main()
