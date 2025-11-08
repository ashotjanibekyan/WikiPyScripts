import re
from typing import List

import pywikibot
import mwparserfromhell

from WikiCheckers.WikiChecker import WikiChecker


class TranslateCiteDate(WikiChecker):
    cite_templates: set[str]
    date_params: List[str] = ['accessdate', 'access-date', 'archivedate', 'archive-date', 'publicationdate',
                              'publication-date', 'doibrokendate', 'doi-brokendate', 'doibroken-date',
                              'doi-broken-date',
                              'date', 'pmcembargodate', 'pmc-embargodate', 'pmcembargo-date', 'pmc-embargo-date']
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

    def __init__(self, site: pywikibot.Site, cite_templates):
        super().__init__(site)

        cite_redirects = []
        for tt in cite_templates:
            t = pywikibot.Page(self.site, 'Template:' + tt)
            redirects = t.backlinks(filter_redirects=True)
            for r in redirects:
                cite_redirects.append(self.norm_title(r.title(with_ns=False)))

        self.cite_templates = set(cite_templates + cite_redirects)

    @staticmethod
    def norm_title(title):
        title = title.strip()
        nm = title[0].upper() + title[1:]
        return nm

    def get_hy_from_named_month(self, year, month, day=None):
        month_str = None
        if month.title() in self.en_to_hy_month_names:
            month_str = self.en_to_hy_month_names[month.title()]
        if month in self.en_to_hy_month_names:
            month_str = self.en_to_hy_month_names[month]
        if month.lower() in self.hy_months:
            month_str = month.lower()
        if month.lower() + 'ի' in self.hy_months:
            month_str = month.lower() + 'ի'
        if month_str:
            if day:
                return f'{year} թ․ {month_str} {day}'
            else:
                month_str = month_str[:-1]
                return f'{year} թ․ {month_str}'
        return None

    def get_hy_date(self, date):
        date = date.strip()
        # m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date)
        # if m:
        #     year = int(m.group(1))
        #     month = int(m.group(2))
        #     day = int(m.group(3))
        #     if day > 31 or month > 12 or day < 1 or month < 1:
        #         return date
        #     return f'{year} թ․ {self.index_to_hy_month_names[month]} {day}'
        m = re.match(r'^(\w+) (\d{1,2}), (\d{4})$', date)
        if m:
            year = int(m.group(3))
            month = m.group(1)
            day = int(m.group(2))
            if day > 31 or day < 1:
                return date
            result = self.get_hy_from_named_month(year, month, day)
            if result:
                return result
        m = re.match(r'^(\d{1,2}) (\w+) (\d{4})$', date)
        if m:
            year = int(m.group(3))
            month = m.group(2)
            day = int(m.group(1))
            if day > 31 or day < 1:
                return date
            result = self.get_hy_from_named_month(year, month, day)
            if result:
                return result
        m = re.match(r'^(\w+) (\d{4})$', date)
        if m:
            year = int(m.group(2))
            month = m.group(1)
            result = self.get_hy_from_named_month(year, month)
            if result:
                return result
        m = re.match(r'^(\d{4}) (\w+)$', date)
        if m:
            year = int(m.group(1))
            month = m.group(2)
            result = self.get_hy_from_named_month(year, month)
            if result:
                return result
        return date

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        for node in parsed.filter_templates(recursive=True):
            if not isinstance(node, mwparserfromhell.wikicode.Template):
                continue
            if self.norm_title(node.name) in self.cite_templates:
                for param_name in self.date_params:
                    if not node.has(param_name):
                        continue
                    param = node.get(param_name)
                    node.add(param_name, self.get_hy_date(param.value))
        return str(parsed), 'ծանոթագրության կաղապարում ամսաթվի թարգմանություն/ձևաչափի ուղղում'
