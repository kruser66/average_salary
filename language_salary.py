import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable
from itertools import count


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
    api_url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'X-Api-App-Id': secret_key,
    }
    params = {
        'town': town,
        'page': page,
        'keywords': [[1, 'and', search_text]],
    }

    response = requests.get(api_url, headers=headers, params=params)
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


def calculate_totals(salaries, vacancies_found):
    processed = [elem for elem in salaries if elem and elem > 20000]
    vacancies_processed = len(processed)

    if vacancies_processed:
        average_salary = int(sum(processed) / vacancies_processed)
    else:
        average_salary = 0

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }


def collect_average_salary_hh(code_languages, town):
    average_salary = {}

    for code in code_languages:
        salaries = []

        for page in count():
            vacancies = search_vacancies_hh(
                search_text=f'Разработчик {code}',
                area=town,
                page=page,
                clusters=True,
                search_field='name'
            )
            salaries.extend(
                [
                    predict_rub_salary_hh(vacancy)
                    for vacancy in vacancies['items']
                    if vacancy['salary']
                ]
            )
            if page >= vacancies['pages'] - 1:
                break

        average_salary[code] = calculate_totals(salaries, vacancies['found'])

    return average_salary


def collect_average_salary_sj(secret_key, code_languages, town):
    average_salary = {}

    for code in code_languages:
        salaries = []

        for page in count():
            vacancies = search_vacancies_sj(
                secret_key,
                search_text=f'Разработчик {code}',
                town=town,
                page=page
            )
            salaries.extend(
                [
                    predict_rub_salary_sj(vacancy)
                    for vacancy in vacancies['objects']
                ]
            )
            if not vacancies['more']:
                break

        average_salary[code] = calculate_totals(salaries, vacancies['total'])

    return average_salary


def output_formatted_table(average_salaries, title=''):
    table_rows = []
    table_title = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]

    table_rows.append(table_title)
    for code, total in average_salaries.items():
        table_rows.append(
            [
                code,
                total['vacancies_found'],
                total['vacancies_processed'],
                total['average_salary']
            ]
        )

    table = AsciiTable(table_rows)
    table.title = title

    return table.table


if __name__ == '__main__':

    load_dotenv()
    secret_key = os.getenv('SUPERJOB_API_SECRET_KEY')

    # Для поиска по HeadHunter искать id здесь: https://api.hh.ru/areas
    hh_id_area = 1
    hh_title_name = 'Москва'

    sj_town_name = 'Москва'

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
        average_salaries_hh = collect_average_salary_hh(
            code_languages, hh_id_area
        )

    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    print(output_formatted_table(
        average_salaries_hh, f' HeadHunter {hh_title_name}')
    )

    try:
        average_salaries_sj = collect_average_salary_sj(
            secret_key,
            code_languages,
            sj_town_name,
        )
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    print(output_formatted_table(
        average_salaries_sj, f' SuperJob {sj_town_name}')
    )
