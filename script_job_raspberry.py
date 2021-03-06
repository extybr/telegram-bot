#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests


def search_jobs(telegram_id, telegram_role: str, telegram_profession: str, telegram_area: str,
                telegram_period: str) -> None:
    """
    Парсер вакансий с сайта hh.ru
    :return: None
    """
    try:
        professional_role = f'&professional_role={telegram_role}' if len(telegram_role) > 0 else ''
        text_profession = f'&text={telegram_profession}'  # ключевое слово для поиска
        area = telegram_area  # регион
        publication_time = 'order_by=publication_time&'
        period = telegram_period  # период поиска
        url = (f'https://api.hh.ru/vacancies?clusters=true&st=searchVacancy&enable_snippets=true&'
               f'{publication_time}period={period}&only_with_salary=false{professional_role}'
               f'{text_profession}&page=0&per_page=100&area={area}&responses_count_enabled=true')

        headers = {
            'Host': 'api.hh.ru',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        print('Headhunter: парсинг вакансий')
        count_vacancies = requests.get(url, headers).json().get('found')
        print('Найдено результатов:', count_vacancies)
        with open(f'vacancies/{telegram_id}.txt', 'w', encoding='utf-8') as text:
                text.write('Найдено результатов: ' + str(count_vacancies) + '\n\n')
        pages = count_vacancies // 100
        for page in range(int(period)):
            url = (f'https://api.hh.ru/vacancies?clusters=true&st=searchVacancy&enable_snippets='
                   f'true&order_by=publication_time&period={period}&only_with_salary=false'
                   f'{professional_role}{text_profession}&page={page}&per_page=100&area={area}'
                   f'&responses_count_enabled=true')
            result = requests.get(url, headers)
            results = result.json()
            items = results.get('items', {})
            text = open(f'vacancies/{telegram_id}.txt', 'a', encoding='utf-8')
            for index in items:
                company = index['employer']['name']
                name = index['name']
                link = index["alternate_url"]
                types = index['type']['name']
                date = index['published_at'][:10]
                address = index['area']['name']
                schedule = index['schedule']['name']
                if index['address']:
                    address = index['address']['raw']
                salary = index['salary']
                if count_vacancies > 0:
                    if salary:
                        from_salary = salary['from']
                        to_salary = salary['to']
                        if not isinstance(from_salary, int):
                            from_salary = '😜'
                        if not isinstance(to_salary, int):
                            to_salary = '🚀'
                        output = (f'  {company}  '.center(50, '*') + f'\n\n🚮   Профессия: {name}'
                                  f'\n😍   Зарплата: {from_salary} - {to_salary}\n⚜   Ссылка: '
                                  f'{link}\n🐯   /{types}/   -🌼-   дата публикации: {date}   -🌻-'
                                  f'   график работы: {schedule.lower()}\n🚘   Адрес: {address}\n')
                        # text.write(output)
                        text.write(output.center(50, '*') + '\n')
                    else:
                        output = (f'  {company}  '.center(50, '*') + f'\n\n🚮   Профессия: {name}\n😍'
                                  f'   Зарплата: не указана\n⚜   Ссылка: {link}\n🐯   /{types}/'
                                  f'   -🌼-   дата публикации: {date}   -🌻-   график работы: '
                                  f'{schedule.lower()}\n🚦   Количество откликов для вакансии: '
                                  f'\n🚘   Адрес: {address}\n')
                        # text.write(output)
                        text.write(output.center(50, '*') + '\n')
            text.close()
    except OSError as error:
        print(f'Статус: проблемы с доступом в интернет\n{error}')
