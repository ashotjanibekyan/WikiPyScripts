import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

page = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/հավանաբար մահացած ապրող անձինք')


def get_pages_by_category():
    query = '''SELECT page_title
FROM page
WHERE page_title != 'Գլխավոր_էջ'
AND page_id IN (SELECT cl_from FROM categorylinks WHERE cl_to LIKE '%_մահեր' OR cl_to LIKE '%_թաղվածներ')
AND page_id IN (SELECT cl_from FROM categorylinks WHERE cl_to IN ('Ապրող_անձինք'))
AND page_namespace = 0
AND page_is_redirect = 0
ORDER BY page_title'''
    titles = []
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            titles.append(helpers.get_cell_txt(r[0]))
    return titles


titles = get_pages_by_category()

page.text = '\n'.join(['# [[' + title + ']]' for title in titles])
page.save(summary='թարմացում', botflag=False)
