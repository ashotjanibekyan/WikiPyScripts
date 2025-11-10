import toolforge, re, time
import pywikibot as pw

import helpers
from helpers import matrix_to_wikitable

hywiki = pw.Site('hy', 'wikipedia')

query = '''SELECT DISTINCT page_title, cl_to 
FROM   categorylinks JOIN page ON page_id = cl_from 
WHERE  page_namespace = 2 
       AND cl_to NOT IN (SELECT page_title 
                         FROM   page JOIN page_props ON page_id = pp_page 
                         WHERE  pp_propname = 'hiddencat') 
       AND cl_to IN (SELECT cl_to 
                     FROM   categorylinks JOIN page ON page_id = cl_from 
                     WHERE  page_namespace = 0);'''

conn = toolforge.connect('hywiki')

skip = {}
skipPage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/հոդվածների հետ նույն կատեգորիայում ապրող մասնակցային էջեր/անտեսել')
if skipPage.exists():
    skipPages = skipPage.text.splitlines()
    for line in skipPages:
        line = re.sub(r'^\* *(.+) *\n?', r'\1', line)
        line = line.replace('Մասնակից:', '')
        skip[line] = True

with conn.cursor() as cur:
    cur.execute(query)
    results = cur.fetchall()
    text = [['Մասնակցային էջ', 'Կատեգորիա']]
    for r in results:
        try:
            if helpers.get_cell_txt(r[0]) not in skip:
                thispage = pw.Page(hywiki, 'Մասնակից:' + helpers.get_cell_txt(r[0]))
                thispage.text = re.sub(r'\[\[([Կկ]ատեգորիա|[Cc]ategory):', '[[:Կատեգորիա:', thispage.text)
                thispage.save(summary='Կատեգորիան հեռացնում եմ ավազարկղից')
                time.sleep(30)
                if list(filter(lambda x: not x.isHiddenCategory(), list(thispage.categories()))):
                    text.append(
                        ['[[Մասնակից:' + helpers.get_cell_txt(r[0]) + ']]', '[[:Կատեգորիա:' + helpers.get_cell_txt(r[1]) + ']]'])
        except:
            continue
    p = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/հոդվածների հետ նույն կատեգորիայում ապրող մասնակցային էջեր')
    p.text = matrix_to_wikitable(text)
    p.save(summary='թարմացում', botflag=False)
