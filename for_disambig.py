import pywikibot as pw
import toolforge

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/այլ կիրառումների համար')

sql = '''WITH DisambigPages AS
  (SELECT DISTINCT REPLACE(p.page_title, '_(այլ_կիրառումներ)', '') AS title
   FROM page AS p
   JOIN categorylinks cl ON p.page_id = cl.cl_from
   WHERE cl.cl_to = 'Բազմիմաստության_փարատման_էջեր'
     AND p.page_namespace = 0
   UNION SELECT *
   FROM (
         VALUES ('Ավետարան'), ('Ճառընտիր'), ('Մաշտոց_ձեռաց'), ('Ծաղկավոր_բույսերի_ցեղեր'), ('Մատենագրութիւնք'), 
                ('Քարոզգիրք'), ('Տաղարան'), ('Հայսմավուրք'), ('Մաշտոց'), ('Ճաշոց'), 
                ('Ֆուտբոլի_Եվրոպայի_առաջնություն_2012'), ('Շարակնոց'), ('Սաղմոսարան'), ('Կանոնգիրք_հայոց'), 
                ('Արցախյան_պատերազմում_զոհված_ազատամարտիկների_ցանկ')) AS title)
SELECT CASE
           WHEN LOCATE('(', page_title) > 0
                AND page_title LIKE "%(%)" THEN SUBSTRING(page_title, 1, LOCATE('(', page_title) - 2)
           ELSE page_title
       END AS extracted_text,
       GROUP_CONCAT(page_title
                    ORDER BY page_title ASC SEPARATOR '\n') AS all_page_titles,
       COUNT(*) AS C
FROM page
WHERE page_is_redirect = 0
  AND page_namespace = 0
  AND SUBSTRING(page_title, 1, LOCATE('(', page_title) - 2) NOT IN (SELECT title FROM DisambigPages)
  AND page_title NOT IN (SELECT title FROM DisambigPages)
GROUP BY extracted_text
HAVING C > 2
AND C < 100
ORDER BY C DESC'''

with conn.cursor() as cur:
    cur.execute(sql)
    results = cur.fetchall()
    text = ''
    for r in results:
        try:
            batch = ''
            titles = helpers.get_cell_txt(r[1]).split('\n')
            for title in titles:
                batch += f'\n# [[{title}]]'
            batch += f" - [[{helpers.get_cell_txt(r[0])} (այլ կիրառումներ)]]"
            text += batch
        except Exception as ex:
            print(ex)
    page.text = text
    page.save('թարմացում', botflag=False)
