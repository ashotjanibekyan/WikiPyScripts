import toolforge
import pywikibot as pw

import helpers
from helpers import matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/էջ-քննարկում վերահղման անհամապատասխանություն')

sql = '''SELECT p1.page_title,
  (SELECT rd_title
   FROM redirect
   WHERE rd_from = p1.page_id) p1red,
       p2.page_title,
  (SELECT rd_title
   FROM redirect
   WHERE rd_from = p2.page_id) p2red
FROM page p1
JOIN page p2 ON p1.page_title = p2.page_title
WHERE p1.page_namespace = 0
  AND p2.page_namespace = 1
  AND p1.page_is_redirect != p2.page_is_redirect
ORDER BY p1.page_title'''

with conn.cursor() as cur:
    table = [['Հոդված', 'Հոդվածը վերահղվում է դեպի', 'Քննարկում', 'Քննարկումը վերահղվում է դեպի']]
    cur.execute(sql)
    results = cur.fetchall()
    for r in results:
        article_title = f"[[{helpers.get_cell_txt(r[0])}]]"
        article_redirects_to = f"[[{helpers.get_cell_txt(r[1])}]]" if r[1] else ''
        talk_title = f"[[Քննարկում:{helpers.get_cell_txt(r[2])}]]"
        talk_redirects_to = f"[[Քննարկում:{helpers.get_cell_txt(r[3])}]]" if r[3] else ''

        table.append([article_title, article_redirects_to, talk_title, talk_redirects_to])
    page.text = matrix_to_wikitable(table)
    page.save(summary='թարմացում', botflag=False)
