from itertools import count
from time import sleep
from terminaltables import AsciiTable
import requests


def create_table(language_params, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакасий обработано', 'Средняя зарплата']
    ]
    for language, params in language_params.items():
        table_data.append([language, params['vacancies_found'], params['vacancies_processed'], params['average_salary']])
    table = AsciiTable(table_data, title)
    print(table.table)


def get_superjob_vacancies(language):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    salaries = []
    headers = {
        'X-Api-App-Id': 'v3.r.137493167.b05769075f242ec71b29249267fb0a1bc85c3022.6f80984fd5ee94c155d3ece5da6091466411f267'
    }
    for page in count(0):
        payload = {'town': 'Москва', 'keyword': language, 'page': page}
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        for vacancy in response.json()['objects']:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            salary_currency = vacancy['currency']
            predicted_salary = predict_rub_salary(salary_from, salary_to, salary_currency)
            if predicted_salary:
                salaries.append(predicted_salary)
            print(vacancy['profession'], vacancy['town'], predicted_salary)
        if not response.json()['more']:
            break
    vacancies_processed = len(salaries)
    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return {
        "vacancies_found": response.json()['total'],
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }


def get_vacancies(language):
    url = "https://api.hh.ru/vacancies"
    salaries = []
    for page in count(0):
        payload = {'text': language, 'area': '1', 'page': page}
        response = requests.get(url, params=payload)
        print(response.json())
        response.raise_for_status()
        print(page)
        sleep(0.2)
        for vacancy in response.json()['items']:
            if not vacancy['salary']:
                continue
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            salary_currency = vacancy['salary']['currency']
            predicted_salary = predict_rub_salary(salary_from, salary_to, salary_currency)
            if predicted_salary:
                salaries.append(predicted_salary)
        if page >= response.json()['pages']-1:
            break
    vacancies_processed = len(salaries)

    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return {
        "vacancies_found": response.json()['found'],
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }


def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != 'RUR' and salary_currency != 'rub':
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


if __name__ == "__main__":
    language_params_headhunter = {}
    language_params_superjob = {}
    languages = ['Python', 'Java', 'JavaScript', 'c', 'c#', 'c++', 'ruby', 'js', 'go']
    for language in languages:
        language_params_superjob[language] = get_superjob_vacancies(language)
        language_params_headhunter[language] = get_vacancies(language)
    create_table(language_params_superjob, 'SuperJob Moscow')
    create_table(language_params_headhunter, 'HeadHunter Moscow')