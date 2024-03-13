import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/անմասնակից մասնակցային էջեր')

query = '''SELECT concat(if(page_namespace = 2, "# [[Մասնակից", "# [[Մասնակցի քննարկում"), ":", page_title, ']]') AS title
FROM page
WHERE (page_namespace = 3
       OR page_namespace = 2)
  AND REPLACE(SUBSTRING_INDEX(page_title, '/', 1), '_', ' ') NOT IN
    (SELECT user_name
     FROM user)
  AND page_is_redirect = 0
ORDER BY title'''

with conn.cursor() as cur:
    text = ''
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
