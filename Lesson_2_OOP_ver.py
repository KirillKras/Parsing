from abc import ABCMeta, abstractmethod
import re
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pprint import pprint


class VacancynParserBase(metaclass=ABCMeta):

    @abstractmethod
    def