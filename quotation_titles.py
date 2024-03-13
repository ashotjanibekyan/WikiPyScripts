import re

import toolforge
import pywikibot as pw

import helpers

site = pw.Site('hy', 'wikipedia')
page = pw.Page(site, 'Վիքիպեդիա:Ցանկեր/չակերտներով հոդվածներ')


def get_articles():
    query = '''SELECT page_title
FROM page
WHERE page_is_redirect = 0
	AND page_namespace = 0
    AND page_title LIKE "%«%»%"'''
    conn = toolforge.connect('hywiki')
    titles = []
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            titles.append(helpers.get_cell_txt(r[0]))
    return titles


def make_list(titles):
    data = [['Հոդված', 'Առանց չակերտ', 'defaultsort']]
    for title in titles:
        p = pw.Page(site, title)
        r = pw.Page(site, re.sub(r'[«»]', '', title))
        ds = p.defaultsort()
        data.append([f'[[{p.title()}]]', f'[[{r.title()}]]', ds])
    return data


quotation_titles = get_articles()
quotation_titles.sort()
page.text = helpers.matrix_to_wikitable(make_list(quotation_titles))
page.save('թարմացում', botflag=False)