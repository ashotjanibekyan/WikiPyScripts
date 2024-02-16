import re

import toolforge
import pywikibot as pw

import helpers
from helpers import nsMap

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

exceptions_page = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/դատարկ էջեր/բացառություններ')
exceptions = re.sub(r'\* *', '', exceptions_page.text).split('\n')

sql_empty = 'SELECT page_title, page_namespace FROM page WHERE page_len = 0 AND page_namespace != 2 and page_namespace != 3 ORDER BY page_title;'
sql_very_short = 'SELECT page_title, page_namespace, page_len FROM page WHERE page_len > 0 AND page_len <= 10 AND page_namespace != 2 and page_namespace != 3 ORDER BY page_title;'

text = 'Ցանկում ներառված են Հայերեն Վիքիպեդիայի բոլոր դատարկ էջերը՝ բացառությամբ այն էջերը, որոնք մասնակից մասնակցի քննարկում անվանատարածքներում են։\n'
with conn.cursor() as cur:
    cur.execute(sql_empty)
    results = cur.fetchall()
    for r in results:
        title = f"{nsMap[r[1]]}:{r[0].decode('utf-8')}"
        if title in exceptions:
            continue
        line = f"# [[{title}]]\n"
        if nsMap[r[1]] == 'Պատկեր' or nsMap[r[1]] == 'Կատեգորիա':
            line = line.replace('# [[', '# [[:')
        text += line

with conn.cursor() as cur:
    cur.execute(sql_very_short)
    results = cur.fetchall()
    table = [['Էջ', 'Չափ']]
    for r in results:
        title = f"{nsMap[r[1]]}:{r[0].decode('utf-8')}"
        if title in exceptions:
            continue
        page = pw.Page(hywiki, title)
        if r[1] == 1 and page.exists() and re.match(r'\{\{[^}]+}}', page.text.strip()):
            continue
        line = f"[[{title}]]\n"
        if nsMap[r[1]] == 'Պատկեր' or nsMap[r[1]] == 'Կատեգորիա':
            line = line.replace('[[', '[[:')
        table.append([line, r[2]])

    text += '\n== Շատ փոքր էջեր (1-10 բայթ) ==\n'
    text += ('1-10 բայթ էջերը, բացառության մասնակցային էջերի և այն քննարկման էջերի, որոնք ունեն մեկ կաղապար։ Որոշ '
             'կաղապարների դեպքում շատ փոքր չափը նորմալ է, բայց եթե կաղապարները հայտնվել են այս ցանկում, '
             'ապա դրանք կատեգորիա չունեն, ինչը խնդիր է։\n')
    text += helpers.matrix_to_wikitable(table)

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/դատարկ էջեր')
page.text = text
page.save('թարմացում', botflag=False)
