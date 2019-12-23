from pprint import pprint
from vacancy.vacancy_parser import VacancyParserHH, VacancyParserSJ
from vacancy.bd_converters import VacancyMongoClient
import vacancy.bd_converters


def main():
    vacancy_mongodb = VacancyMongoClient()
    parser = VacancyParserHH(search_string='Data scientist', user_agent_header='chrome', parse_all=True)
    parser.to_mongodb(vacancy_mongodb)


if __name__ == '__main__':
    main()
