from collections import namedtuple

TagFilter = namedtuple('TagFilter', 'tag attrs')
Filter = namedtuple('Filter', 'items source name link date')

filterLenta = Filter(
    items="//div[@class='first-item'] | //div[@class='item']",
    name=".//a[text()]/text()",
    link=".//a[text()]/@href",
    source=None,
    date=None
)

filterYandex = Filter(
    items="//div[@class='card__body']",
    name=".//span[@class='link link_pseudo card__link']/text()",
    source=".//div[@class='card__status card__status_left']/a/text()",
    link="./a/@href",
    date=None
)

filterMail = Filter(
    items= "(//span[@class='item__text'] | //span[@class='photo__title'])",
    name="/text()",
    link="ancestor::a[@href]/@href",
    source="//a[@class='article__param color_blue']/text()",
    date="//time[@class=' js-ago']/@datetime"
)