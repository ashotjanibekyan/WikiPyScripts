import datetime
import re
import sys

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators


def norm_title(title):
    title = title.strip()
    nm = title[0].lower() + title[1:]
    return nm


hywiki: pywikibot.Site = pywikibot.Site('hy', 'wikipedia')

cite_templates = ['cite web', 'cite journal', 'cite news', 'cite book', 'cite AV media', 
                  'cite encyclopedia', 'cite arXiv', 'cite interview', 'cite thesis', 
                  'cite conference', 'cite AV media notes', 'cite press release', 
                  'cite magazine', 'cite mailing list', 'cite techreport', 'cite podcast', 
                  'lien web', 'cite map', 'cite document']

cite_redirects = []

for tt in cite_templates:
    t = pywikibot.Page(hywiki, 'Template:' + tt)
    redirects = t.backlinks(filter_redirects=True)
    for r in redirects:
        cite_redirects.append(norm_title(r.title(with_ns=False)))

templates = set(cite_templates + cite_redirects)

date_params = ['accessdate', 'access-date', 'archivedate', 'archive-date', 'publicationdate', 'publication-date',
               'doibrokendate', 'doi-brokendate', 'doibroken-date', 'doi-broken-date', 'date',
               'pmcembargodate', 'pmc-embargodate', 'pmcembargo-date', 'pmc-embargo-date']

index_to_hy_month_names = {
    1: 'հունվարի',
    2: 'փետրվարի',
    3: 'մարտի',
    4: 'ապրիլի',
    5: 'մայիսի',
    6: 'հունիսի',
    7: 'հուլիսի',
    8: 'օգոստոսի',
    9: 'սեպտեմբերի',
    10: 'հոկտեմբերի',
    11: 'նոյեմբերի',
    12: 'դեկտեմբերի',
}

hy_months = index_to_hy_month_names.values()

en_to_hy_month_names = {
    "January": "հունվարի",
    "February": "փետրվարի",
    "March": "մարտի",
    "April": "ապրիլի",
    "May": "մայիսի",
    "June": "հունիսի",
    "July": "հուլիսի",
    "August": "օգոստոսի",
    "September": "սեպտեմբերի",
    "October": "հոկտեմբերի",
    "November": "նոյեմբերի",
    "December": "դեկտեմբերի",
    "Jan": "հունվարի",
    "Feb": "փետրվարի",
    "Mar": "մարտի",
    "Apr": "ապրիլի",
    "Jun": "հունիսի",
    "Jul": "հուլիսի",
    "Aug": "օգոստոսի",
    "Sep": "սեպտեմբերի",
    "Oct": "հոկտեմբերի",
    "Nov": "նոյեմբերի",
    "Dec": "դեկտեմբերի",
}

def get_hy_from_named_month(year, month, day):
    month_str = None
    if month.title() in en_to_hy_month_names:
        month_str = en_to_hy_month_names[month.title()]
    if month in en_to_hy_month_names:
        month_str = en_to_hy_month_names[month]
    if month.lower() in hy_months:
        month_str = month.lower()
    if month.lower() + 'ի' in hy_months:
        month_str = month.lower() + 'ի'
    if month_str:
        return f'{year} թ․ {month_str} {day}'
    return None


def get_hy_date(date):
    date = date.strip()
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if day > 31 or month > 12:
            return date
        return f'{year} թ․ {index_to_hy_month_names[month]} {day}'
    m = re.match(r'^(\w+) (\d{1,2}), (\d{4})$', date)
    if m:
        year = int(m.group(3))
        month = m.group(1)
        day = int(m.group(2))
        if day > 31:
            return date
        result = get_hy_from_named_month(year, month, day)
        if result:
            return result
    m = re.match(r'^(\d{1,2}) (\w+) (\d{4})$', date)
    if m:
        year = int(m.group(3))
        month = m.group(2)
        day = int(m.group(1))
        if day > 31:
            return date
        result = get_hy_from_named_month(year, month, day)
        if result:
            return result
    return date


def get_all_templates(parsed):
    temps = []
    for temp in parsed.filter_templates(recursive=True):
        temps += get_all_templates(temp)
    return temps


def process_page(p):
    parsed: mwparserfromhell.wikicode = mwparserfromhell.parse(p.text)
    for node in parsed.filter_templates(recursive=True):
        if norm_title(node.name) in templates:
            for param_name in date_params:
                if not node.has(param_name):
                    continue
                param = node.get(param_name)
                node.add(param_name, get_hy_date(param.value))
    return str(parsed)


def treat_page(p):
    new_text = process_page(p)
    if p.text != new_text:
        p.text = new_text
        p.save('ծանոթագրության կաղապարում ամսաթվի թարգմանություն/ձևաչափի ուղղում')


if len(sys.argv) >= 2 and sys.argv[1] == 'full':
    gen = pagegenerators.AllpagesPageGenerator(site=hywiki, start='!', namespace=0, includeredirects=False)
else:
    end = str(hywiki.server_time() - datetime.timedelta(days=2))
    gen = list(set(pagegenerators.RecentChangesPageGenerator(site=hywiki, namespaces=0, end=end)))

for page in gen:
    try:
        treat_page(page)
    except Exception as e:
        print(e)
