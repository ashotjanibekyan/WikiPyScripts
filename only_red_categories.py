import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/միայն կարմիր կատեգորիա ունեցող հոդվածներ')

query = '''SELECT CONCAT('#[[', a.page_title, ']]')
FROM
  (
    SELECT p.page_id,
           p.page_title,
           COUNT(cl.cl_target_id) AS total_categories
    FROM page p
    JOIN categorylinks cl ON p.page_id = cl.cl_from
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE p.page_namespace = 0
      AND lt.lt_namespace = 14
    GROUP BY p.page_id
  ) a
LEFT JOIN
  (
    SELECT cl.cl_from,
           COUNT(*) AS existing_categories
    FROM categorylinks cl
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_namespace = 14
    GROUP BY cl.cl_from
  ) b ON a.page_id = b.cl_from
WHERE b.existing_categories IS NULL
   OR b.existing_categories = 0
ORDER BY a.page_title;'''

with conn.cursor() as cur:
    text = 'Տես նաև՝ [[Վիքիպեդիա:Ցանկեր/գրեթե անկատեգորիա հոդվածներ]]'
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text+='\n' + helpers.get_cell_txt(r[0])
    page.text = text
    page.save(summary='թարմացում', botflag=False)
