import toolforge
import pywikibot as pw

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/միայն կարմիր կատեգորիա ունեցող հոդվածներ')

query = '''SELECT concat('#[[', a.page_title, ']]')
FROM
  (SELECT page_id,
          page_title,
          COUNT(cl_to) AS total_categories
   FROM page
   JOIN categorylinks ON page_id = cl_from
   WHERE page_namespace = 0
   GROUP BY page_id) a
LEFT JOIN
  (SELECT cl_from,
          COUNT(*) AS existing_categories
   FROM categorylinks
   JOIN page ON page_title = cl_to
   AND page_namespace = 14
   GROUP BY cl_from) b ON a.page_id = b.cl_from
WHERE b.existing_categories IS NULL
  OR b.existing_categories = 0
ORDER BY a.page_title'''

with conn.cursor() as cur:
    text = 'Տես նաև՝ [[Վիքիպեդիա:Ցանկեր/գրեթե անկատեգորիա հոդվածներ]]'
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text+='\n' + r[0].decode('utf-8').replace('_', ' ')
    page.text = text
    page.save(summary='թարմացում', botflag=False)
