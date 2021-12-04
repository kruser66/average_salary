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
    print(salary)
    if salary['currency'] == 'RUR':
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

    count_vacancy = {}

    vacancies = search_vacancies(search_text=f'Разработчик Python', area=1)

    average_salaries = [predict_rub_salary(vacancy) for vacancy in vacancies['items']]

    pprint(average_salaries)
