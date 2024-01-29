import toolforge
import pywikibot as pw

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Մասնակից:ԱշոտՏՆՂ/ցանկեր/գրեթե անկատեգորիա հոդվածներ')

query = '''SELECT page_title
FROM page
WHERE page_title != 'Գլխավոր_էջ'
AND page_id NOT IN
    (SELECT cl_from
        FROM categorylinks
        WHERE cl_to NOT LIKE '%այբբենական_կարգով'
            AND cl_to NOT LIKE 'Անավարտ_%'
            AND cl_to NOT LIKE '%_ծնունդներ'
            AND cl_to NOT LIKE '%0_ֆիլմեր'
            AND cl_to NOT LIKE '%1_ֆիլմեր'
            AND cl_to NOT LIKE '%2_ֆիլմեր'
            AND cl_to NOT LIKE '%3_ֆիլմեր'
            AND cl_to NOT LIKE '%4_ֆիլմեր'
            AND cl_to NOT LIKE '%5_ֆիլմեր'
            AND cl_to NOT LIKE '%6_ֆիլմեր'
            AND cl_to NOT LIKE '%7_ֆիլմեր'
            AND cl_to NOT LIKE '%8_ֆիլմեր'
            AND cl_to NOT LIKE '%9_ֆիլմեր'
            AND cl_to NOT LIKE '%_մահեր'
            AND cl_to NOT LIKE '%_ծնվածներ'
            AND cl_to NOT LIKE '%_մահացածներ'
            AND cl_to NOT LIKE '%_թաղվածներ'
            AND cl_to NOT IN ('Ապրող_անձինք')
            AND cl_to NOT IN
                (SELECT page_title
                FROM page
                JOIN categorylinks ON cl_from = page_id
                WHERE cl_to = 'Թաքցված_կատեգորիաներ'))
AND page_id NOT IN
    (SELECT cl_from
        FROM categorylinks
        WHERE cl_to = 'Առանց_կատեգորիայի_հոդվածներ' )
AND page_namespace = 0
AND page_is_redirect = 0
ORDER BY (SELECT count(*) FROM langlinks WHERE ll_from = page_id) DESC'''

with conn.cursor() as cur:
    text = ''
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        text += '\n# [[' + r[0].decode('utf-8').replace('_', ' ') + ']]'
    page.text = text
    page.save(summary='թարմացում', botflag=False)
