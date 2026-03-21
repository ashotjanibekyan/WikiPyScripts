import toolforge
import pywikibot as pw

import helpers
from helpers import matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ հղվող բազմիմաստության փարատման էջեր')


sql = '''WITH DisambigPages AS (
    SELECT DISTINCT p.page_title AS title
    FROM page p
    JOIN categorylinks cl ON p.page_id = cl.cl_from
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_title = 'Բազմիմաստության_փարատման_էջեր'
      AND lt.lt_namespace = 14
      AND p.page_namespace = 0
),
DisambigRedirect AS (
    SELECT DISTINCT p.page_title AS title
    FROM redirect r
    JOIN page p ON r.rd_from = p.page_id
    WHERE p.page_namespace = 0
      AND r.rd_title IN (SELECT title FROM DisambigPages)
),
AllDisamig AS (
    SELECT title FROM DisambigPages
    UNION
    SELECT title FROM DisambigRedirect
)

SELECT lt.lt_title,
       COUNT(*) AS C
FROM pagelinks pl
JOIN page p1 ON p1.page_id = pl.pl_from
JOIN linktarget lt ON pl.pl_target_id = lt.lt_id
WHERE p1.page_is_redirect = 0
  AND p1.page_namespace = 0
  AND lt.lt_title IN (SELECT title FROM AllDisamig)
GROUP BY lt.lt_title
HAVING C > 1
ORDER BY C DESC, lt.lt_title;'''


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
