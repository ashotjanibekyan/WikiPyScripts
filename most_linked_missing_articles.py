import toolforge
import pywikibot as pw
from datetime import date

conn = toolforge.connect('enwiki')

query = '''SELECT Count(*) ll_count, page_title title_en,
  (SELECT ll_title
   FROM langlinks
   WHERE ll_from = page_id
     AND ll_lang = 'ru' ) title_ru
FROM page, langlinks
WHERE ll_from = page_id
  AND (SELECT Count(*) FROM langlinks WHERE ll_from = page_id ) >= 50
  AND page_id NOT IN (SELECT ll_from FROM langlinks WHERE ll_lang = 'hy' )
  AND page_namespace = 0
GROUP BY page_id
ORDER BY ll_count DESC, page_title
LIMIT 3000;
'''

with conn.cursor() as cur:
    cur.execute(query)
    results = cur.fetchall()
    text = date.today().strftime(
        "%Y-%m-%d") + ' դրությամբ ամենաշատ միջլեզվային հղումներն ունեցող հոդվածները, որոնք չկան Հայերեն Վիքիպեդիայում'
    text += '\n{| class="wikitable"\n!մլհ-ների քանակ!!Հոդվածն Անգլերեն Վիքիպեդիայում!!Հոդվածը Ռուսերեն Վիքիպեդիայում'
    for r in results:
        text += '\n|-'
        text += '\n|' + str(r[0])
        text += '\n|[[:en:' + r[1].decode('utf-8') + ']]'
        if r[2]:
            text += '\n|[[:ru:' + r[2].decode('utf-8') + ']]'
        else:
            text += '\n|'
    text += '\n|}'
    page = pw.Page(pw.Site('hy', 'wikipedia'),
                   'Մասնակից:ԱշոտՏՆՂ/ցանկեր/պակասող հոդվածներ ըստ միջլեզվային հղումների քանակի')
    page.text = text
    page.save(summary='թարմացում', botflag=False)
