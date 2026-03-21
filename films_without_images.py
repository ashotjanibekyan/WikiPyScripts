import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ֆիլմեր, որոնք պատկեր չունեն')

query = '''WITH NonFreeImages AS (
    SELECT p.page_title AS title
    FROM page p
    JOIN categorylinks cl ON p.page_id = cl.cl_from
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_title = 'Բոլոր_ոչ_ազատ_պատկերներ'
      AND lt.lt_namespace = 14
),
Movies AS (
    SELECT p.page_id AS movie_id
    FROM page p
    JOIN categorylinks cl ON p.page_id = cl.cl_from
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_title = 'Ֆիլմեր_այբբենական_կարգով'
      AND lt.lt_namespace = 14
      AND p.page_namespace = 0
),
MoviesWithNonFreeImages AS (
    SELECT p.page_id AS movie_with_non_free_image_id
    FROM page p
    JOIN Movies m ON p.page_id = m.movie_id
    JOIN imagelinks il ON p.page_id = il.il_from
    WHERE p.page_is_redirect = 0
      AND p.page_namespace = 0
      AND EXISTS (
          SELECT 1
          FROM NonFreeImages nf
          WHERE il.il_to = nf.title
      )
)
SELECT CONCAT('# [[', p.page_title, ']]')
FROM page p
JOIN Movies m ON p.page_id = m.movie_id
WHERE NOT EXISTS (
    SELECT 1
    FROM MoviesWithNonFreeImages mn
    WHERE p.page_id = mn.movie_with_non_free_image_id
)
ORDER BY p.page_title;'''

with conn.cursor() as cur:
    text = ''
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
