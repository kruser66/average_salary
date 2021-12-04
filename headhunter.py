import requests
from pprint import pprint


def search_vacancies(search_text=''):
    api_url = 'https://api.hh.ru/vacancies'

    params = {
        'area': 1,
        'text': 'Разработчик {}'.format(search_text),
        'search_field': 'name',
        'per_page': 0,
        'clusters': True,
    }
    response = requests.get(api_url, params=params)
    data = response.json()
   
    return data['found']


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

    for code_lauguage in code_lauguages:
        search_result[code_lauguage] = search_vacancies(code_lauguage)

    pprint(search_result)
