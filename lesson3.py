from pprint import pprint
from vacancy_parser import VacancyParserHH, VacancyParserSJ
from bd_converters import VacancyMongoClient
import bd_converters


def main():
    vacancy_mongodb = VacancyMongoClient()
    parser = VacancyParserHH(search_string='Data scientist', user_agent_header='chrome', parse_all=True)
    parser.to_mongodb(vacancy_mongodb)


if __name__ == '__main__':
    main()
