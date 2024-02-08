import pywikibot as pw
from datetime import datetime, timedelta
import calendar
import re
import mwparserfromhell as mwp

commons = pw.Site('commons', 'commons')
hywiki = pw.Site('hy', 'wikipedia')
hywwiki = pw.Site('hyw', 'wikipedia')

def without_comments(wiki_text):
    if wiki_text is None:
        return None
    wikicode = mwp.parse(wiki_text)
    for node in wikicode.nodes[:]:
        if isinstance(node, mwp.nodes.Comment):
            wikicode.remove(node)
    return str(wikicode).strip()

def get_first_param(wiki_text):
    templates = mwp.parse(wiki_text).filter_templates()
    if templates:
        if templates[0].has(1):
            first_param_value = templates[0].get(1).value
            return str(first_param_value).strip()
    return None

def handle_month(year, month):
    for i in range(1, 1 + calendar.monthrange(year, month)[1]):
        str_year = str(year)
        str_month = str(month)
        str_day = str(i)
        if month < 10:
            str_month = '0' + str_month
        if i < 10:
            str_day = '0' + str_day
        title = 'Template:Potd/' + str_year + '-' + str_month + '-' + str_day
        template_in_commons = pw.Page(commons, title)
        if template_in_commons.exists():
            file = without_comments(get_first_param(template_in_commons.text))
            if not file:
                continue
            template_in_hy = pw.Page(hywiki, title)
            if not template_in_hy.exists():
                template_in_hy.text = file + '<noinclude>[[Կատեգորիա:Կաղապարներ:Օրվա պատկեր]]</noinclude>'
                template_in_hy.save(summary='Օրվա պատկերը Վիքիպահեստից')
            template_in_hyw = pw.Page(hywwiki, title)
            if not template_in_hyw.exists():
                template_in_hyw.text = file
                template_in_hyw.save(summary='Օրուան Պատկերը Ուիքիպահեստից')

def plus_minus_month(num):
    today = datetime.now()
    days_in_current_month = calendar.monthrange(today.year, today.month)[1]
    new_month_date = today + num * timedelta(days=days_in_current_month)
    return new_month_date
prev_month_date = plus_minus_month(-1)
this_month_date = plus_minus_month(0)
next_month_date = plus_minus_month(1)

handle_month(prev_month_date.year, prev_month_date.month)
handle_month(this_month_date.year, this_month_date.month)
handle_month(next_month_date.year, next_month_date.month)


