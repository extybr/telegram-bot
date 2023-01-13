from requests import get
from loguru import logger


def search_job(telegram_id, telegram_role: str, telegram_profession: str, telegram_area: str,
               telegram_period: str) -> None:
    """  Парсер вакансий с сайта hh.ru """
    logger.info(f'Переданы параметры: {telegram_id}, {telegram_role}, {telegram_profession}, '
                f'{telegram_area}, {telegram_period}')
    try:
        professional_role = f'&professional_role={telegram_role}' if len(telegram_role) > 1 else ''
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

        logger.info('hh.ru: парсинг вакансий')
        result = get(url, headers)
        results = result.json()
        count_vacancies = results.get('found')
        logger.info(f'Найдено результатов: {count_vacancies}')
        with open(f'vacancies/{telegram_id}.txt', 'w', encoding='utf-8') as text:
            text.write('Найдено результатов: ' + str(count_vacancies) + '\n\n')
        items = results.get('items', {})
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
            # if company == 'Спам Компания'.strip():
            #     continue
            if count_vacancies > 0:
                text = open(f'vacancies/{telegram_id}.txt', 'a', encoding='utf-8')
                if salary:
                    from_salary = salary['from']
                    to_salary = salary['to']
                    if not isinstance(from_salary, int):
                        from_salary = '😜'
                    if not isinstance(to_salary, int):
                        to_salary = '🚀'
                    output = (f'  {company}  '.center(50, '*') + f'\n\n🚮   Профессия: {name}\n😍   '
                              f'Зарплата: {from_salary} - {to_salary}\n⚜   Ссылка: {link}\n🐯   '
                              f'/{types}/   -🌼-   дата публикации: {date}   -🌻-   график работы: '
                              f'{schedule.lower()}\n🚘   Адрес: {address}\n')
                    text.write(output.center(50, '*') + '\n')
                else:
                    output = (f'  {company}  '.center(50, '*') + f'\n\n🚮   Профессия: {name}\n😍'
                              f'   Зарплата: не указана\n⚜   Ссылка: {link}\n🐯   /{types}/'
                              f'   -🌼-   дата публикации: {date}   -🌻-   график работы: '
                              f'{schedule.lower()}\n🚦   Количество откликов для вакансии: '
                              f'\n🚘   Адрес: {address}\n')
                    text.write(output.center(50, '*') + '\n')
                text.close()
    except OSError as error:
        logger.error(f'Статус: проблемы с доступом в интернет\n{error}')


def region_id(region: str) -> str:
    """ Получение id региона """
    logger.info(f'Запрос кода региона: {region}')
    try:
        url = f'https://api.hh.ru/suggests/areas?text={region}'
        headers = {
            'Host': 'api.hh.ru',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        result = get(url, headers)
        results = result.json()
        items = results.get('items', {})
        id_region = [i['id'] for i in items]
        return id_region[0] if len(id_region) > 0 else None
    except OSError as error:
        logger.error(f'Статус: проблемы с доступом в интернет\n{error}')
