from pprint import pprint
from vacancy.vacancy_parser import VacancyParserHH, VacancyParserSJ
from vacancy.bd_converters import VacancyMongoClient
import vacancy.bd_converters


def add_vacancies():
    vacancy_mongodb = VacancyMongoClient()
    parser = VacancyParserHH(search_string='Data scientist', user_agent_header='chrome', parse_all=True)
    parser.to_mongodb(vacancy_mongodb)


def find_vacancies_gr(compensation):
    vacancy_mongodb = VacancyMongoClient()
    for vacancy in vacancy_mongodb.find_vacancy_gt(100000):
        pprint(vacancy)


if __name__ == '__main__':
    find_vacancies_gr(1000000)
