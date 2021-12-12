import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def search_vacancies_hh(search_text, area, page=0,
                        clusters=False, search_field=''):
    api_url = 'https://api.hh.ru/vacancies'

    params = {
        'area': area,
        'text': search_text,
        'search_field': search_field,
        'page': page,
        'clusters': clusters,
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()

    return response.json()


def search_vacancies_sj(secret_key, search_text, town, page=0):
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'X-Api-App-Id': secret_key,
    }
    params = {
        'town': town,
        'page': page,
        'keywords': [[1, 'and', search_text]],
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def predict_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return int((payment_from + payment_to) / 2)
    elif payment_from:
        return int(payment_from * 1.2)
    elif payment_to:
        return int(payment_to * 0.8)


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    payment_from = salary['from']
    payment_to = salary['to']
    currency = salary['currency']
    if currency == 'RUR':
        return predict_salary(payment_from, payment_to)


def predict_rub_salary_sj(vacancy):
    payment_from = vacancy['payment_from']
    payment_to = vacancy['payment_to']
    currency = vacancy['currency']
    if currency == 'rub':
        return predict_salary(payment_from, payment_to)


def calculation_of_values(salaries, vacancies_found):
    processed = [elem for elem in salaries if elem and elem > 20000]
    vacancies_processed = len(processed)

    if vacancies_processed:
        average_salary = int(sum(processed) / vacancies_processed)

    values = {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }

    return values


def collect_average_salary_hh(code_languages, town):
    search_result = {}

    for code in code_languages:

        vacancies = search_vacancies_hh(
            search_text=f'Разработчик {code}',
            area=town,
            clusters=True,
            search_field='name'
        )
        vacancies_found = vacancies['found']

        salaries = [predict_rub_salary_hh(vacancy)
                    for vacancy in vacancies['items']
                    if vacancy['salary']]

        for page in range(1, vacancies['pages'] + 1):
            vacancies = search_vacancies_hh(
                search_text=f'Разработчик {code}',
                area=town,
                page=page,
                search_field='name'
            )
            salaries.extend(
                [predict_rub_salary_hh(vacancy)
                    for vacancy in vacancies['items']
                    if vacancy['salary']]
            )

        search_result[code] = calculation_of_values(salaries, vacancies_found)

    return search_result


def collect_average_salary_sj(secret_key, code_languages, town):
    search_result = {}

    for code in code_languages:
        search_result[code] = {}
        vacancies = search_vacancies_sj(
            secret_key,
            search_text=f'Разработчик {code}',
            town=town
        )
        vacancies_found = vacancies['total']

        salaries = [predict_rub_salary_sj(vacancy)
                    for vacancy in vacancies['objects']]

        page = 1
        while vacancies['more']:
            vacancies = search_vacancies_sj(
                secret_key,
                search_text=f'Разработчик {code}',
                town=town,
                page=page
            )
            salaries.extend(
                [predict_rub_salary_sj(vacancy)
                    for vacancy in vacancies['objects']]
            )
            page += 1

        search_result[code] = calculation_of_values(salaries, vacancies_found)

    return search_result


def result_formatted_out(result, title=''):
    data = []
    table_title = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]

    data.append(table_title)
    for code, value in result.items():
        data.append(
            [
                code,
                value['vacancies_found'],
                value['vacancies_processed'],
                value['average_salary']
            ]
        )

    table = AsciiTable(data)
    table.title = title
    print(table.table)


if __name__ == '__main__':

    load_dotenv()
    secret_key = os.getenv('SUPERJOB_API_SECRET_KEY')

    '''
    id региона (Москва) или населенного пункта для поиска
    по HeadHunter искать здесь: https://api.hh.ru/areas
    '''
    area = 1
    title_hh = 'Москва'

    # Имя города для поиска по SuperJob
    town = 'Москва'

    code_languages = [
        'Java',
        'JavaScript',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Swift',
        'TypeScript',
        'Go',
        'Scala',
    ]

    try:
        result_hh = collect_average_salary_hh(code_languages, area)

    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    result_formatted_out(result_hh, f' HeadHunter {title_hh}')

    try:
        result_sj = collect_average_salary_sj(
            secret_key,
            code_languages,
            town
        )
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    result_formatted_out(result_sj, f' SuperJob {town}')
