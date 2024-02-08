import pywikibot as pw
import calendar
from datetime import datetime
from dateutil import relativedelta

from helpers import without_comments, get_first_param

commons = pw.Site('commons', 'commons')
hywiki = pw.Site('hy', 'wikipedia')
hywwiki = pw.Site('hyw', 'wikipedia')


def handle_month(year, month):
    for i in range(1, 1 + calendar.monthrange(year, month)[1]):
        str_year = str(year)
        str_month = f'0{month}' if month < 10 else str(month)
        str_day = f'0{i}' if i < 10 else str(i)
        title = f'Template:Potd/{str_year}-{str_month}-{str_day}'
        template_in_commons = pw.Page(commons, title)
        if not template_in_commons.exists():
            continue
        file = without_comments(get_first_param(template_in_commons.text))
        if not file:
            continue
        file = file.replace("_", " ")
        template_in_hy = pw.Page(hywiki, title)
        template_in_hy.text = file + '<noinclude>[[Կատեգորիա:Կաղապարներ:Օրվա պատկեր]]</noinclude>'
        template_in_hy.save(summary=f'Օրվա պատկերը Վիքիպահեստից, [[:commons:{title}]]')

        template_in_hyw = pw.Page(hywwiki, title)
        template_in_hyw.text = file
        template_in_hyw.save(summary=f'Օրուան Պատկերը Ուիքիպահեստից, [[:commons:{title}]]')


def plus_minus_month(num):
    return datetime.now() + relativedelta.relativedelta(months=num)


prev_prev_month_date = plus_minus_month(-2)
prev_month_date = plus_minus_month(-1)
this_month_date = plus_minus_month(0)
next_month_date = plus_minus_month(1)
next_next_month_date = plus_minus_month(2)

handle_month(prev_prev_month_date.year, prev_prev_month_date.month)
handle_month(prev_month_date.year, prev_month_date.month)
handle_month(this_month_date.year, this_month_date.month)
handle_month(next_month_date.year, next_month_date.month)
handle_month(next_next_month_date.year, next_next_month_date.month)
