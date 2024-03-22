import pywikibot as pw
from datetime import date

import helpers
site = pw.Site('hy', 'wikipedia')

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
HAVING ll_count > 60
ORDER BY ll_count DESC, page_title;'''

header = date.today().strftime("%Y-%m-%d") + ' դրությամբ ամենաշատ միջլեզվային հղումներն ունեցող հոդվածները, որոնք չկան Հայերեն Վիքիպեդիայում'
cols = ['մլհ-ների քանակ', 'Հոդվածն Անգլերեն Վիքիպեդիայում', 'Հոդվածը Ռուսերեն Վիքիպեդիայում']
col_filters = [str, lambda x: f'[[:en:{x}]]', lambda x: f'[[:ru:{x}]]']
page = pw.Page(site,'Վիքիպեդիա:Ցանկեր/պակասող հոդվածներ ըստ միջլեզվային հղումների քանակի')
helpers.sql_to_page('enwiki', query, page, header, cols, col_filters)
