import toolforge
import pywikibot as pw

from helpers import matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքինախագիծ:Մաթեմատիկա/Կարմիր հղումներ')

sql = '''WITH AllMainTitle AS
  (SELECT page_title AS title
   FROM page
   WHERE page_namespace = 0),
     AllMathTitles AS
  (SELECT DISTINCT page_title AS math_page_title
   FROM templatelinks
   JOIN linktarget ON lt_id = tl_target_id
   JOIN page ON page_id = tl_from
   WHERE lt_title = "Վիքինախագիծ_Մաթեմատիկա")
SELECT pl_title,
       count(*) c
FROM pagelinks
JOIN page ON page_id = pl_from
WHERE pl_namespace = 0
  AND page_namespace = 0
  AND pl_title not in
    (SELECT title
     FROM AllMainTitle)
  AND page_title in
    (SELECT math_page_title
     FROM AllMathTitles)
GROUP BY pl_title
HAVING c > 4
ORDER BY c DESC'''

with conn.cursor() as cur:
    table = [['Հղումներ', 'Հոդված']]
    cur.execute(sql)
    page.text = 'Ստորև ներկայացված են մաթեմատիկային վերաբերող հոդվածներում պահանջված հոդվածները։ Հնարավոր է, որ հոդվածների մի մասը արդեն գոյություն ունի այլ անունով, այդ դեպքում հարկավոր է վերահղում տալ։ Ցուցակը տեսակավորված է ըստ հոդվածների պահանջարկի (կարմիր հղումների քանակի)։\n'
    results = cur.fetchall()
    for r in results:
        table.append([r[1], f"[[{r[0].decode('utf-8').replace('_', ' ')}]]"])
    page.text = matrix_to_wikitable(table)
    page.save(summary='թարմացում', botflag=False)

