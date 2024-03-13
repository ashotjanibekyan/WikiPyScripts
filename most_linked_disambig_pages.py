import toolforge
import pywikibot as pw

import helpers
from helpers import matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ հղվող բազմիմաստության փարատման էջեր')


sql = '''WITH DisambigPages AS
  (SELECT DISTINCT p.page_title AS title
   FROM page AS p
   JOIN categorylinks cl ON p.page_id = cl.cl_from
   WHERE cl.cl_to = 'Բազմիմաստության_փարատման_էջեր' AND p.page_namespace = 0 ),
     DisambigRedirect AS
  (SELECT DISTINCT p.page_title title
   FROM redirect
   JOIN page AS p ON rd_from = p.page_id
   WHERE p.page_namespace = 0
     AND rd_title IN
       (SELECT title
        FROM DisambigPages) ),
     AllDisamig AS
  (SELECT title
   FROM DisambigPages
   UNION SELECT title
   FROM DisambigRedirect)
   
SELECT pl_title,
       count(*) as C
FROM pagelinks
JOIN page AS p1 ON p1.page_id = pl_from
AND p1.page_is_redirect = 0
WHERE pl_title in (SELECT title FROM AllDisamig) AND p1.page_namespace = 0
GROUP BY pl_title
HAVING c > 1
ORDER BY C DESC, pl_title'''


with conn.cursor() as cur:
    text = 'Տես նաև՝ [[Վիքիպեդիա:Ցանկեր/ամենաշատ բազմիմաստ հղում ունեցող հոդվածներ]]\n'
    table = [['Հոդված', 'Քանակ']]
    cur.execute(sql)
    results = cur.fetchall()
    for r in results:
        title = helpers.get_cell_txt(r[0])
        table.append([
            f'[[{title}]] ([[Սպասարկող:Այստեղհղվողէջերը/{title}|հղումներ]])',
            str(r[1])
        ])
    page.text = text + matrix_to_wikitable(table)
    page.save(summary='թարմացում', botflag=False)
