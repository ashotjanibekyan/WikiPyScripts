import pywikibot as pw
from datetime import date
from dateutil.relativedelta import relativedelta
import re

two_days = date.today() + relativedelta(days=-2)
one_days = date.today() + relativedelta(days=-1)
hywiki = pw.Site('hy', 'wikipedia')
gen = list(hywiki.newpages(total=0,
                           end=str(two_days) + 'T00:00:00.000Z',
                           start=str(one_days) + 'T00:00:00.000Z',
                           namespaces=0))

for page in gen:
    if page[0].exists() and page[0].toggleTalkPage().exists() and '<ref' in page[0].text:
        if '{{ԹՀ' in page[0].toggleTalkPage().text:
            categories = [i.title() for i in page[0].categories()]
            m = list(set(re.findall(r'\{\{ԹՀ\|([^|]+)\|([^}|]+)', page[0].toggleTalkPage().text)))
            if m and 'Կատեգորիա:Բնօրինակում անաղբյուր հոդվածներ' not in categories:
                has_source = False
                for lang in m:
                    source_wiki = pw.Site(lang[0], 'wikipedia')
                    source_page = pw.Page(source_wiki, lang[1])
                    if '<ref' in source_page.text:
                        has_source = True
                        break
                if not has_source:
                    page[0].text = page[0].text + '\n[[Կատեգորիա:Բնօրինակում անաղբյուր հոդվածներ]]'
                    page[0].save(summary='+[[Կատեգորիա:Բնօրինակում անաղբյուր հոդվածներ]]', botflag=False)
