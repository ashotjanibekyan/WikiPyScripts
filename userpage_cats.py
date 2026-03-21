import toolforge, re, time
import pywikibot as pw

import helpers
from helpers import matrix_to_wikitable

hywiki = pw.Site('hy', 'wikipedia')

query = '''SELECT DISTINCT p.page_title, lt.lt_title
FROM categorylinks cl
JOIN page p ON p.page_id = cl.cl_from
JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
WHERE p.page_namespace = 2

  AND lt.lt_title NOT IN (
      SELECT p2.page_title
      FROM page p2
      JOIN page_props pp ON pp.pp_page = p2.page_id
      WHERE pp.pp_propname = 'hiddencat'
  )

  AND lt.lt_title IN (
      SELECT lt2.lt_title
      FROM categorylinks cl2
      JOIN page p3 ON p3.page_id = cl2.cl_from
      JOIN linktarget lt2 ON lt2.lt_id = cl2.cl_target_id
      WHERE p3.page_namespace = 0
  );'''

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
