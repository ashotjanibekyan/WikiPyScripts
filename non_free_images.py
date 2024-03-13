import toolforge
import pywikibot as pw

import helpers
from helpers import nsMap, matrix_to_wikitable

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')


def save_overused_images_list(page, query):
    text = '''Տես նաև՝
* [[Վիքիպեդիա:Ցանկեր/մեծ նկարներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable"\n!Պատկեր!!Օգտագործում'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|' + helpers.get_cell_txt(r[0])
            text += '\n|' + str(r[1])
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում', botflag=False)


def save_overuse_pages_list(page, query):
    text = '''Տես նաև՝
* [[Վիքիպեդիա:Ցանկեր/մեծ նկարներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        table = [['Էջ', 'Ոչ ազատ պատկերներ']]
        page_files_map = {}
        for r in results:
            using_page = nsMap[r[1]] + ':' + helpers.get_cell_txt(r[0])
            file = 'Պատկեր:' + helpers.get_cell_txt(r[2])
            page_files_map.setdefault(using_page, []).append(file)

        table += [
            [f'[[{key}]]', '\n' + '\n'.join(f'* [[:{file}]]' for file in value)]
            for key, value in sorted(page_files_map.items())
        ]
        text += '\n' + matrix_to_wikitable(table)
    page.text = text
    page.save(summary='թարմացում', botflag=False)


def save_non_main_images_list(page, query):
    text = '''Տես նաև՝
* [[Վիքիպեդիա:Ցանկեր/մեծ նկարներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable sortable"\n!Պատկեր!!Էջ!!Բեռնման ամսաթիվ'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|[[:Պատկեր:' + helpers.get_cell_txt(r[2]) + ']]'
            text += '\n|[[' + nsMap[r[1]] + ':' + helpers.get_cell_txt(r[0]) + ']]'
            text += '\n|' + helpers.get_cell_txt(r[3])
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում', botflag=False)


def save_living_peoples_images_list(page, query):
    text = '''Տես նաև՝
* [[Վիքիպեդիա:Ցանկեր/մեծ նկարներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Վիքիպեդիա:Ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]'''
    text += '\n{| class="wikitable sortable"\n!Հոդված!!Պատկեր'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|[[' + helpers.get_cell_txt(r[0]) + ']]'
            text += '\n|[[:Պատկեր:' + helpers.get_cell_txt(r[1]) + ']]'
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում', botflag=False)


overusedPage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ')
overusePage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ')
nonMainPage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս')
livingPeoplesPage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում')

overusedQuery = '''SELECT Concat("[[:file:", Replace(page_title, '_', ' '), "]]"),
       Count(*)
FROM   imagelinks
       JOIN (SELECT page_id,
                    page_title
             FROM   page
             WHERE  page_namespace = 6) AS pgtmp
         ON pgtmp.page_title = il_to
GROUP  BY il_to
HAVING Count(*) > 1
ORDER  BY Count(*) DESC, il_to;'''

overusePagesQuery = '''SELECT (SELECT p1.page_title 
        FROM   page AS p1 
        WHERE  p1.page_id = il_from) article, 
       (SELECT p1.page_namespace 
        FROM   page AS p1 
        WHERE  p1.page_id = il_from) ns, 
       il_to 
FROM   imagelinks 
WHERE  il_from IN (SELECT il_from 
                   FROM   imagelinks 
                   WHERE  EXISTS (SELECT 1 
                                  FROM   image 
                                  WHERE  img_name = il_to) 
                   GROUP  BY il_from 
                   HAVING Count(il_to) > 1 
                   ORDER  BY Count(il_to) DESC) 
       AND EXISTS (SELECT 1 
                   FROM   image 
                   WHERE  img_name = il_to)'''

nonMainQuery = '''SELECT (SELECT p1.page_title 
        FROM   page AS p1 
        WHERE  p1.page_id = il_from) article, 
       (SELECT p1.page_namespace 
        FROM   page AS p1 
        WHERE  p1.page_id = il_from) ns, 
       il_to,
       (SELECT img_timestamp 
        FROM   image 
        WHERE  img_name = il_to) up
FROM   imagelinks 
WHERE  il_from_namespace > 0
       AND EXISTS (SELECT 1 
                   FROM   image 
                   WHERE  img_name = il_to)
ORDER BY il_to, article, ns'''

livingPeoplesQuery = '''SELECT DISTINCT p.page_title, i.il_to FROM page p
INNER JOIN categorylinks c1 ON p.page_id = c1.cl_from AND c1.cl_to = "Ապրող_անձինք"
INNER JOIN imagelinks i ON i.il_from = p.page_id 
						AND i.il_from_namespace = 0
INNER JOIN page i_p ON i.il_to = i_p.page_title
INNER JOIN categorylinks c2 ON i_p.page_id = c2.cl_from AND c2.cl_to = "Բոլոր_ոչ_ազատ_պատկերներ"'''

save_overused_images_list(overusedPage, overusedQuery)
save_overuse_pages_list(overusePage, overusePagesQuery)
save_non_main_images_list(nonMainPage, nonMainQuery)
save_living_peoples_images_list(livingPeoplesPage, livingPeoplesQuery)
