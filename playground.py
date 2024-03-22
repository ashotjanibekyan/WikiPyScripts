import datetime

import pywikibot as pw
from pywikibot import pagegenerators as pg
from tqdm import tqdm

import helpers


def main(project, delta, gen, prf):
    site = pw.Site('hy', project)
    end = str(site.server_time() - delta)

    last_edited_by_ip = [['Հոդված', 'Տարբ', 'IP', 'Ամսաթիվ']]
    skip_users = set(map(lambda x: x['name'], list(site.allusers(group='bot'))))
    skip_users.add('CommonsDelinker')
    skip_users.add('MusikyanBot')
    pbar = tqdm(total=len(gen))
    for page in gen:
        pbar.update()
        if not page.exists():
            continue
        for revision in page.revisions(total=10):
            user = revision['user']
            if user in skip_users:
                continue
            if revision['anon']:
                last_edited_by_ip.append([f'[[{page.title()}]]',
                                          f'[https://hy.{project}.org/w/index.php?diff=prev&oldid={revision["revid"]} տարբ]',
                                          f'[[Սպասարկող:Ներդրումները/{user}|{user}]]',
                                          str(revision['timestamp'])])
            else:
                break

    list_page = pw.Page(site, f'{project}:Ցանկեր/վերջին անգամ խմբագրել է IP/{prf}')
    if len(last_edited_by_ip) > 1:
        list_page.text = helpers.matrix_to_wikitable(last_edited_by_ip)
        list_page.save('թարմացում', botflag=False)


if __name__ == '__main__':
    namespaces = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10, 11, 12, 13, 14, 15, 100, 101, 102, 103, 104, 105, 106, 107, 710, 711, 828, 829]
    delta = datetime.timedelta(days=365)
    project = 'wikisource'
    site = pw.Site('hy', project)
    end = str(site.server_time() - delta)
    # gen = list(set(pg.RecentChangesPageGenerator(site=site, namespaces=namespaces, end=end)))

    for ns in namespaces:
        pages = list(site.allpages(start='!', namespace=ns))
        main(project, delta, pages, ns)
