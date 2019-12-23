import re
from collections import namedtuple

# Классы фильтров интересующих данных
TagFilter = namedtuple('TagFilter', 'tag attrs')
Filter = namedtuple('Filter', 'vacancy position company city compensation link next')

filterHH = Filter(
        vacancy=TagFilter(tag='div', attrs={'data-qa': 'vacancy-serp__vacancy'}),
        position=TagFilter(tag='a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}),
        company=TagFilter(tag='a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}),
        city=TagFilter(tag='span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}),
        compensation=TagFilter(tag='div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}),
        link=TagFilter(tag='a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}),
        next=TagFilter(tag='a', attrs={'data-qa': 'pager-next'}))

filterSJ = Filter(
        vacancy=TagFilter(tag='div',
                          attrs={'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'}),
        position=TagFilter(tag='div',
                           attrs={'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}),
        company=TagFilter(tag='span',
                          attrs={
                              'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _3e53o _15msI'}),
        city=TagFilter(tag='span',
                       attrs={'class': '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _3e53o'}),
        compensation=TagFilter(tag='span',
                               attrs={
                                   'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}),
        link=TagFilter(tag='a', attrs=re.compile(r'icMQ_ _1QIBo')),
        next=TagFilter(tag='a', attrs={'rel': 'next'}))