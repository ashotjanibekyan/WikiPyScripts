import datetime

import pywikibot as pw
from pywikibot import pagegenerators as pg
from tqdm import tqdm

import helpers

site = pw.Site('hy', 'wikipedia')
end = str(site.server_time() - datetime.timedelta(days=7))
gen = list(set(pg.RecentChangesPageGenerator(site=site, namespaces=[0], end=end)))

last_edited_by_ip = [['Հոդված', 'Տարբ', 'IP', 'Ամսաթիվ']]
skip_users = set(map(lambda x: x['name'], list(site.allusers(group='bot'))))
skip_users.add('CommonsDelinker')
skip_users.add('MusikyanBot')
pbar = tqdm(total=len(gen))
for page in gen:
    pbar.update()
    if not page.exists():
        continue
    for revision in page.revisions(endtime=end):
        user = revision['user']
        if user in skip_users:
            continue
        if 'temp' in dict(revision):
            last_edited_by_ip.append([f'[[{page.title()}]]',
                                      f'[https://hy.wikipedia.org/w/index.php?diff=prev&oldid={revision["revid"]} տարբ]',
                                      f'[[Սպասարկող:Ներդրումները/{user}|{user}]]',
                                     str(revision['timestamp'])])
        else:
            break

list_page = pw.Page(site, 'Վիքիպեդիա:Ցանկեր/վերջին անգամ խմբագրել է IP')
list_page.text = helpers.matrix_to_wikitable(last_edited_by_ip)
list_page.save('թարմացում', botflag=False)
