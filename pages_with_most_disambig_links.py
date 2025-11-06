import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ամենաշատ բազմիմաստ հղում ունեցող հոդվածներ')

query = '''WITH DisambigPages AS
  (SELECT DISTINCT p.page_title AS title
   FROM page AS p
   JOIN categorylinks cl ON p.page_id = cl.cl_from
   WHERE cl.cl_to = 'Բազմիմաստության_փարատման_էջեր'
     AND p.page_namespace = 0 ),
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
SELECT concat('# [[', mainPage.page_title, ']] - ', count(*))
FROM page AS mainPage
JOIN pagelinks ON mainPage.page_id = pl_from
JOIN linktarget ON lt_id = pl_target_id
JOIN AllDisamig AS allDisambig ON lt_title = allDisambig.title
WHERE mainPage.page_namespace = 0
  AND mainPage.page_id NOT IN
    (SELECT cl_from
     FROM categorylinks
     WHERE cl_to = 'Ազգանուններ_այբբենական_կարգով')
GROUP BY mainPage.page_title
HAVING count(*) > 2
ORDER BY count(*) DESC, mainPage.page_title'''

with conn.cursor() as cur:
    text = 'Տես նաև՝ [[Վիքիպեդիա:Ցանկեր/շատ հղվող բազմիմաստության փարատման էջեր]]'
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
