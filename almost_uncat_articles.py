import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/գրեթե անկատեգորիա հոդվածներ')

query = '''SELECT p.page_title
FROM page p
WHERE p.page_title != 'Գլխավոր_էջ'
AND p.page_namespace = 0
AND p.page_is_redirect = 0

AND p.page_id NOT IN (
    SELECT cl.cl_from
    FROM categorylinks cl
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_title NOT LIKE '%այբբենական_կարգով'
        AND lt.lt_title NOT LIKE 'Անավարտ_%'
        AND lt.lt_title NOT LIKE '%_ծնունդներ'
        AND lt.lt_title NOT LIKE '%0_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%1_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%2_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%3_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%4_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%5_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%6_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%7_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%8_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%9_ֆիլմեր'
        AND lt.lt_title NOT LIKE '%_մահեր'
        AND lt.lt_title NOT LIKE '%_ծնվածներ'
        AND lt.lt_title NOT LIKE '%_մահացածներ'
        AND lt.lt_title NOT LIKE '%_թաղվածներ'
        AND lt.lt_title != 'Ապրող_անձինք'
        AND lt.lt_title NOT IN (
            SELECT p2.page_title
            FROM page p2
            JOIN categorylinks cl2 ON cl2.cl_from = p2.page_id
            JOIN linktarget lt2 ON lt2.lt_id = cl2.cl_target_id
            WHERE lt2.lt_title = 'Թաքցված_կատեգորիաներ'
        )
)

AND p.page_id NOT IN (
    SELECT cl.cl_from
    FROM categorylinks cl
    JOIN linktarget lt ON lt.lt_id = cl.cl_target_id
    WHERE lt.lt_title = 'Առանց_կատեգորիայի_հոդվածներ'
)

ORDER BY p.page_title;'''

with conn.cursor() as cur:
    text = ''
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n# [[' + helpers.get_cell_txt(r[0]) + ']]'
    page.text = text
    page.save(summary='թարմացում', botflag=False)
