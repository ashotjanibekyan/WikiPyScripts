import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ամենաշատ բազմիմաստ հղում ունեցող հոդվածներ')

query = '''WITH DisambigPages AS (
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

SELECT CONCAT('# [[', mainPage.page_title, ']] - ', COUNT(*))
FROM page mainPage
JOIN pagelinks pl ON mainPage.page_id = pl.pl_from
JOIN linktarget lt ON lt.lt_id = pl.pl_target_id
JOIN AllDisamig ad ON lt.lt_title = ad.title
WHERE mainPage.page_namespace = 0
  AND mainPage.page_id NOT IN (
      SELECT cl.cl_from
      FROM categorylinks cl
      JOIN linktarget lt2 ON lt2.lt_id = cl.cl_target_id
      WHERE lt2.lt_title = 'Ազգանուններ_այբբենական_կարգով'
        AND lt2.lt_namespace = 14
  )
GROUP BY mainPage.page_title
HAVING COUNT(*) > 2
ORDER BY COUNT(*) DESC, mainPage.page_title;'''

with conn.cursor() as cur:
    text = 'Տես նաև՝ [[Վիքիպեդիա:Ցանկեր/շատ հղվող բազմիմաստության փարատման էջեր]]'
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
