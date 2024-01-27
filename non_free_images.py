import toolforge
import pywikibot as pw

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

nsMap = {
    0: "",
    1: "Քննարկում",
    2: "Մասնակից",
    3: "Մասնակցի քննարկում",
    4: "Վիքիպեդիա",
    5: "Վիքիպեդիայի քննարկում",
    6: "Պատկեր",
    7: "Պատկերի քննարկում",
    8: "MediaWiki",
    9: "MediaWiki քննարկում",
    10: "Կաղապար",
    11: "Կաղապարի քննարկում",
    12: "Օգնություն",
    13: "Օգնության քննարկում",
    14: "Կատեգորիա",
    15: "Կատեգորիայի քննարկում",
    100: "Պորտալ",
    101: "Պորտալի քննարկում",
    102: "Վիքինախագիծ",
    103: "Վիքինախագծի քննարկում",
    118: "Սևագիր",
    119: "Սևագրի քննարկում",
    828: "Մոդուլ",
    829: "Մոդուլի քննարկում",
    2300: "Gadget",
    2301: "Gadget talk",
    2302: "Gadget definition",
    2303: "Gadget definition talk",
    -2: "Մեդիա",
    -1: "Սպասարկող"
}


def getOverusedImages(page, query):
    text = '''Տես նաև՝
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/մեծ նկարներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable"\n!Պատկեր!!Օգտագործում'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|' + r[0].decode('utf-8')
            text += '\n|' + str(r[1])
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում')


def get_overuse_pages(page, query):
    text = '''Տես նաև՝
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/մեծ նկարներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable"\n!Էջ!!Ոչ ազատ պատկերներ'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        if len(results) == 0:
            return
        workingTitle = ''
        block = ''
        for r in results:
            if not r[0].decode('utf-8') == workingTitle:
                workingTitle = r[0].decode('utf-8')
                text += block
                block = '\n|-'
                block += '\n|[[' + nsMap[r[1]] + ':' + r[0].decode('utf-8') + ']]'
                block += '\n|'
            block += '\n* [[:Պատկեր:' + r[2].decode('utf-8') + ']]'
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում')


def get_large_images(page, query):
    text = '''Տես նաև՝
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable"\n!Պատկեր!!width!!height'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|[[:Պատկեր:' + r[0].decode('utf-8') + ']]'
            text += '\n|' + str(r[1])
            text += '\n|' + str(r[2])
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում')


def non_main_images(page, query):
    text = '''Տես նաև՝
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/մեծ նկարներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում]]'''
    text += '\n{| class="wikitable sortable"\n!Պատկեր!!Էջ!!Բեռնման ամսաթիվ'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|[[:Պատկեր:' + r[2].decode('utf-8') + ']]'
            text += '\n|[[' + nsMap[r[1]] + ':' + r[0].decode('utf-8') + ']]'
            text += '\n|' + str(r[3].decode('utf-8'))
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում')


def get_living_peoples_images(page, query):
    text = '''Տես նաև՝
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/մեծ նկարներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ]]
* [[Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս]]'''
    text += '\n{| class="wikitable sortable"\n!Հոդված!!Պատկեր'
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            text += '\n|-'
            text += '\n|[[' + r[0].decode('utf-8') + ']]'
            text += '\n|[[:Պատկեր:' + r[1].decode('utf-8') + ']]'
        text += '\n|}'
    page.text = text
    page.save(summary='թարմացում')


overusedPage = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ անգամ օգտագործվող ոչ ազատ պատկերներ')
overusePage = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/1+ ոչ ազատ պատկեր ունեցող հոդվածներ')
largePage = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/մեծ նկարներ')
nonMainPage = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ հոդվածից դուրս')
livingPeoplesPage = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/ոչ ազատ պատկերներ ապրող անձանց հոդվածներում')

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

largeQuery = "select img_name, img_width, img_height from image where img_width > 600 or img_height > 600"

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
order by up'''

livingPeoplesQuery = '''SELECT DISTINCT p.page_title, i.il_to FROM page p
INNER JOIN categorylinks c1 ON p.page_id = c1.cl_from AND c1.cl_to = "Ապրող_անձինք"
INNER JOIN imagelinks i ON i.il_from = p.page_id 
						AND i.il_from_namespace = 0
INNER JOIN page i_p ON i.il_to = i_p.page_title
INNER JOIN categorylinks c2 ON i_p.page_id = c2.cl_from AND c2.cl_to = "Բոլոր_ոչ_ազատ_պատկերներ"'''

get_large_images(largePage, largeQuery)
getOverusedImages(overusedPage, overusedQuery)
get_overuse_pages(overusePage, overusePagesQuery)
non_main_images(nonMainPage, nonMainQuery)
get_living_peoples_images(livingPeoplesPage, livingPeoplesQuery)
