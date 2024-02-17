import toolforge
import pywikibot as pw

import helpers
from helpers import get_cell_txt

hywiki, ruwiki, enwiki = helpers.get_wikipedias('hy', 'ru', 'en')

query = '''SELECT page_title,
       (SELECT ll_title FROM langlinks WHERE ll_from = page_id AND ll_lang = 'en') en_title,
       (SELECT ll_title FROM langlinks WHERE ll_from = page_id AND ll_lang = 'ru') ru_title,
	   page_len
FROM page
WHERE page_namespace = 0
  AND page_is_redirect = 0
  AND page_title != 'Գլխավոր_էջ'
  AND page_title NOT LIKE "%_դար"
  AND page_title NOT LIKE "Մ.թ.ա._%"
  AND page_id NOT IN
    (SELECT tl_from
     FROM templatelinks
     WHERE tl_target_id IN
         (SELECT lt_id
          FROM linktarget
          WHERE (lt_title = 'Բազմիմաստություն'
                 OR lt_title = 'Տարվա_նավարկում'
                 OR lt_title = 'Մեծ_Հայքի_վարչական_բաժանում'
                 OR lt_title = 'Գիրք:ՀՀՖՕՀՏԲ')
            AND lt_namespace = 10))
  AND page_id NOT IN
    (SELECT cl_from
     FROM categorylinks
     WHERE cl_to = 'Նյութեր_տեղանունների_բառարանից'
       OR cl_to = 'Ազգանուններ_այբբենական_կարգով')
ORDER BY page_len ASC
LIMIT 2000;'''

total = 'Ցակից հեռացվել են «Նյութեր տեղանունների բառարանից» և «Ազգանուններ այբբենական կարգով» կատեգորիաների հոդվածները։ Նաև Բազմիմաստություն, Տարվա նավարկում, և Գիրք:ՀՀՖՕՀՏԲ կաղապարն ունեցող հոդվածները։\n'

conn = toolforge.connect('hywiki')
data = [['Հայերեն', 'Հայերեն չափ', 'Անգլերեն', 'Անգլերեն չափ', 'Ռուսերեն', 'Ռուսերեն չափ']]
with conn.cursor() as cur:
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        hy_title = get_cell_txt(r[0])
        en_title = get_cell_txt(r[1])
        ru_title = get_cell_txt(r[2])
        hy_len = get_cell_txt(r[3])
        data.append([hy_title, hy_len, en_title, 0, ru_title, 0])

en_sizes = helpers.get_size_many(enwiki, list(filter(lambda x: x, map(lambda x: x[2], data))))
ru_sizes = helpers.get_size_many(ruwiki, list(filter(lambda x: x, map(lambda x: x[4], data))))

for d in data:
    if d[2] in en_sizes:
        d[3] = en_sizes[d[2]]
    if d[4] in ru_sizes:
        d[5] = ru_sizes[d[4]]

totalsubpage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ կարճ հոդվածներ')
totalsubpage.text = total + helpers.matrix_to_wikitable(data)
totalsubpage.save(summary='թարմացում', botflag=False)
