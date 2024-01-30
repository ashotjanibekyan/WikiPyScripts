import toolforge
import pywikibot as pw

from helpers import matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/շատ հղվող բազմիմաստության փարատման էջեր')


sql = '''SELECT pl_title,
       count(*) as C
FROM pagelinks
JOIN page AS p1 ON p1.page_id = pl_from
AND p1.page_is_redirect = 0
WHERE pl_title in
    (SELECT p2.page_title
     FROM page AS p2
     JOIN categorylinks ON p2.page_id = cl_from
     WHERE cl_to = "Բազմիմաստության_փարատման_էջեր")
  AND p1.page_namespace = 0
GROUP BY pl_title
HAVING c > 1
ORDER BY C DESC'''


with conn.cursor() as cur:
    table = [['Հոդված', 'Քանակ']]
    cur.execute(sql)
    results = cur.fetchall()
    for r in results:
        title = r[0].decode('utf-8').replace('_', ' ')
        table.append([
            f'[[{title}]] ([[Սպասարկող:Այստեղհղվողէջերը/{title}|հղումներ]])',
            str(r[1])
        ])
    page.text = matrix_to_wikitable(table)
    page.save(summary='թարմացում', botflag=False)
