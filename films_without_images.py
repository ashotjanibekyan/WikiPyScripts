import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ֆիլմեր, որոնք պատկեր չունեն')

query = '''WITH NonFreeImages AS
  (SELECT page_title AS title
   FROM page AS p
   JOIN categorylinks cl ON p.page_id = cl.cl_from
   WHERE cl.cl_to = 'Բոլոր_ոչ_ազատ_պատկերներ'),
     Movies AS
  (SELECT page_id AS movie_id
   FROM page AS p
   JOIN categorylinks cl ON p.page_id = cl.cl_from
   WHERE cl.cl_to = 'Ֆիլմեր_այբբենական_կարգով'
     AND p.page_namespace = 0),
     MoviesWithNonFreeImages AS
  (SELECT page_id AS movie_with_non_free_image_id
   FROM page p
   JOIN Movies AS m ON p.page_id = m.movie_id
   JOIN imagelinks il ON p.page_id = il.il_from
   WHERE p.page_is_redirect = 0
     AND p.page_namespace = 0
     AND EXISTS (
       SELECT 1
       FROM NonFreeImages nf
       WHERE il.il_to = nf.title))
SELECT concat('# [[', p.page_title, ']]')
FROM page p
JOIN Movies m ON p.page_id = m.movie_id
WHERE NOT EXISTS (
    SELECT 1
    FROM MoviesWithNonFreeImages mn
    WHERE p.page_id = mn.movie_with_non_free_image_id)
ORDER BY p.page_title'''

with conn.cursor() as cur:
    text = ''
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
