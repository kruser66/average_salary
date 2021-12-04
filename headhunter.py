import requests
from pprint import pprint


def search_vacancies(search_text, area, clusters=False):
    api_url = 'https://api.hh.ru/vacancies'

    params = {
        'area': area,
        'text': search_text,
        'search_field': 'name',
        'clusters': clusters,
    }

    response = requests.get(api_url, params=params)
    if response.ok:
        return response.json()


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if salary and salary['currency'] == 'RUR':
        if salary['from'] and salary['to']:
            return int((salary['from'] + salary['to']) / 2)
        elif salary['from']:
            return int(salary['from'] * 1.2)
        elif salary['to']:
            return int(salary['to'] * 0.8)


if __name__ == '__main__':

    code_lauguages = [
        'Java',
        'JavaScript',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Swift',
        'Kotlin',
        'Go',
        'Scala',
    ]

    search_result = {}

    for code in code_lauguages:
        
        search_result[code] = {}
        
        vacancies = search_vacancies(search_text=f'Разработчик {code}', area=1, clusters=True)
        salaries = [predict_rub_salary(vacancy) for vacancy in vacancies['items']]
        salaries = [elem for elem in salaries if elem]

        search_result[code]['vacancies_found'] = vacancies['found']
        search_result[code]['vacancies_processed'] = len(salaries)
        search_result[code]['average_salary'] = int(sum(salaries) / len(salaries))

    pprint(search_result)
