import requests
from pprint import pprint

AREA = 1 # id региона или населенного пункта https://api.hh.ru/areas

def search_vacancies(search_text, area, page=0, clusters=False, search_field=''):
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
        print('Parse for ', code)
        search_result[code] = {}

        vacancies = search_vacancies(search_text=f'Разработчик {code}', area=AREA, search_field='name')
        salaries = [predict_rub_salary(vacancy) for vacancy in vacancies['items']]
        search_result[code]['vacancies_found'] = vacancies['found']
        for page in range(1,vacancies['pages']+1):
            vacancies = search_vacancies(search_text=f'Разработчик {code}', area=AREA, page=page, search_field='name')
            salaries.extend([predict_rub_salary(vacancy) for vacancy in vacancies['items']])
        
        search_result[code]['vacancies_found'] = len(salaries)
        salaries = [elem for elem in salaries if elem and elem > 40000]

        search_result[code]['vacancies_processed'] = len(salaries)
        search_result[code]['average_salary'] = int(sum(salaries) / len(salaries))
        
    pprint(search_result)
