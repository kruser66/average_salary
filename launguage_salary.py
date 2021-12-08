import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def search_vacancies_hh(search_text, area, page=0, clusters=False, search_field=''):
    api_url = 'https://api.hh.ru/vacancies'

    params = {
        'area': area,
        'text': search_text,
        'search_field': search_field,
        'page': page,
        'clusters': clusters,
    }

    response = requests.get(api_url, params=params)
    if response.ok:
        return response.json()
    else:
        response.raise_for_status()
        return {'items':[]}


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
    if response.ok:
        return response.json()
    else:
        response.raise_for_request()
        return {'objects': []}


def predict_salary(payment_from, payment_to, currency):
    if currency == 'rub' or currency == 'RUR':
        if payment_from and payment_to:
            return int((payment_from + payment_to) / 2)
        elif payment_from:
            return int(payment_from * 1.2)
        elif payment_to:
            return int(payment_to * 0.8)


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if salary:
        payment_from = salary['from']
        payment_to = salary['to']
        currency = salary['currency']

        return predict_salary(payment_from, payment_to, currency)


def predict_rub_salary_sj(vacancy):
    payment_from = vacancy['payment_from']
    payment_to = vacancy['payment_to']
    currency = vacancy['currency']
    
    return predict_salary(payment_from, payment_to, currency)


def data_collection(search_result, salaries):
    search_result['vacancies_found'] = len(salaries)
    salaries = [elem for elem in salaries if elem and elem > 20000]

    search_result['vacancies_processed'] = len(salaries)
    search_result['average_salary'] = int(sum(salaries) / len(salaries))


def collect_average_salary_hh(code_lauguages, town):
    search_result = {}

    for code in code_lauguages:
        search_result[code] = {}

        vacancies = search_vacancies_hh(search_text=f'Разработчик {code}', area=town, search_field='name')
        salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies['items']]

        for page in range(1,vacancies['pages'] + 1):
            vacancies = search_vacancies_hh(search_text=f'Разработчик {code}', area=town, page=page, search_field='name')
            salaries.extend([predict_rub_salary_hh(vacancy) for vacancy in vacancies['items']])

        data_collection(search_result[code], salaries)        
        
    return search_result


def collect_average_salary_sj(secret_key, code_lauguages, town):
    search_result = {}

    for code in code_lauguages:
        search_result[code] = {}
        vacancies = search_vacancies_sj(secret_key, search_text=f'Разработчик {code}', town=town)
        salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies['objects']]

        page = 1
        while vacancies['more']:
            vacancies = search_vacancies_sj(secret_key, search_text=f'Разработчик {code}', town=town, page=page)
            salaries.extend([predict_rub_salary_sj(vacancy) for vacancy in vacancies['objects']])
            page += 1
        
        data_collection(search_result[code], salaries)        
        
    return search_result


def result_formatted_out(result, title=''):
    data = []
    data.append(['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'])
    for code, value in result.items():
        data.append([code, value['vacancies_found'], value['vacancies_processed'], value['average_salary']])

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

    code_launguages = [
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

    result_hh = collect_average_salary_hh(code_launguages, area)
    result_formatted_out(result_hh, f' HeadHunter {title_hh}')

    result_sj = collect_average_salary_sj(secret_key, code_launguages, town)
    result_formatted_out(result_sj, f' SuperJob {town}')
