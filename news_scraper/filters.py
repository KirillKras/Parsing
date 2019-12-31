from collections import namedtuple

TagFilter = namedtuple('TagFilter', 'tag attrs')
Filter = namedtuple('Filter', 'url items topic source link date')

filterLenta = Filter(
    url="https://lenta.ru",
    items="//div[@class='first-item'] | //div[@class='item']",
    topic=".//a[text()]/text()",
    link=".//a[text()]/@href",
    source=None,
    date=None
)

filterYandex = Filter(
    url="https://news.yandex.ru",
    items="//div[@class='card__body']",
    topic=".//span[@class='link link_pseudo card__link']/text()",
    source=".//div[@class='card__status card__status_left']/a/text()",
    link="./a/@href",
    date=None
)

filterMail = Filter(
    url="https://news.mail.ru",
    items= "(//span[@class='item__text'] | //span[@class='photo__title'])",
    topic="/text()",
    link="ancestor::a[@href]/@href",
    source="//a[@class='article__param color_blue']/text()",
    date="//time[@class=' js-ago']/@datetime"
)