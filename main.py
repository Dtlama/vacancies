from dotenv import load_dotenv
from itertools import count
from time import sleep
from terminaltables import AsciiTable
import requests
import os


def create_table(language_params, title):
    table_payload = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for language, params in language_params.items():
        table_data.append([language, params['vacancies_found'], params['vacancies_processed'], params['average_salary']])
    table = AsciiTable(table_payload, title)


def get_superjob_vacancies_statistics(language, sj_apikey):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    salaries = []
    headers = {
        'X-Api-App-Id': sj_apikey
    }
    for page in count(0):
        payload = {'town': 'Москва', 'keyword': language, 'page': page}
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        response_content = response.json()
        for vacancy in response_content['objects']:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            salary_currency = vacancy['currency']
            predicted_salary = predict_rub_salary(salary_from, salary_to, salary_currency)
            if predicted_salary:
                salaries.append(predicted_salary)
            print(vacancy['profession'], vacancy['town'], predicted_salary)
        if not response_content['more']:
            break
    vacancies_processed = len(salaries)
    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return {
        "vacancies_found": response_content['total'],
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }


def get_vacancies_statistics(language):
    url = "https://api.hh.ru/vacancies"
    salaries = []
    for page in count(0):
        payload = {'text': language, 'area': '1', 'page': page}
        response = requests.get(url, params=payload)
        response.raise_for_status()
        response_content = response.json()
        sleep(0.2)
        for vacancy in response_content['items']:
            if not vacancy['salary']:
                continue
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            salary_currency = vacancy['salary']['currency']
            predicted_salary = predict_rub_salary(salary_from, salary_to, salary_currency)
            if predicted_salary:
                salaries.append(predicted_salary)
        if page >= response_content['pages']-1:
            break
    vacancies_processed = len(salaries)

    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return {
        "vacancies_found": response_contain['found'],
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
    load_dotenv()
    sj_apikey = os.environ['SUPERJOB_APIKEY']
    language_params_headhunter = {}
    language_params_superjob = {}
    languages = ['Python', 'Java', 'JavaScript', 'c', 'c#', 'c++', 'ruby', 'js', 'go']
    for language in languages:
        language_params_superjob[language] = get_superjob_vacancies_statistics(language, sj_apikey)
        language_params_headhunter[language] = get_vacancies_statistics(language)
    create_table(language_params_superjob, 'SuperJob Moscow')
    create_table(language_params_headhunter, 'HeadHunter Moscow')
