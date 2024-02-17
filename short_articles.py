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
  AND page_len < 1000
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
ORDER BY page_len ASC'''

total = "Ցակից հեռացվել են «Նյութեր տեղանունների բառարանից» և «Ազգանուններ այբբենական կարգով» կատեգորիաների հոդվածները։ Նաև Բազմիմաստություն, Տարվա նավարկում, և Գիրք:ՀՀՖՕՀՏԲ կաղապարն ունեցող հոդվածները։\n"
total += "* [https://pageviews.wmcloud.org/massviews/?platform=all-access&agent=user&source=wikilinks&range=this-month&sort=views&direction=1&view=list&target=https://hy.wikipedia.org/wiki/%25D5%258E%25D5%25AB%25D6%2584%25D5%25AB%25D5%25BA%25D5%25A5%25D5%25A4%25D5%25AB%25D5%25A1:%25D5%2591%25D5%25A1%25D5%25B6%25D5%25AF%25D5%25A5%25D6%2580/%25D5%25B7%25D5%25A1%25D5%25BF_%25D5%25AF%25D5%25A1%25D6%2580%25D5%25B3_%25D5%25B0%25D5%25B8%25D5%25A4%25D5%25BE%25D5%25A1%25D5%25AE%25D5%25B6%25D5%25A5%25D6%2580 Հոդվածների ցանկն ըստ դիտումների]\n"
total += "* [https://petscan.wmflabs.org/?psid=27011339 Ցանկի անաղբյուր հոդվածներ]\n"

conn = toolforge.connect('hywiki')
data = [['Հայերեն հոդված', 'Հայերեն չափ', 'Անգլերեն հոդված', 'Անգլերեն չափ', 'Ռուսերեն հոդված', 'Ռուսերեն չափ']]
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

for d in data[1:]:
    d[0] = f'[[{d[0]}]]'
    if d[2] in en_sizes:
        d[3] = en_sizes[d[2]]
        d[2] = f'[[:en:{d[2]}]]'
    else:
        d[3] = ''
    if d[4] in ru_sizes:
        d[5] = ru_sizes[d[4]]
        d[4] = f'[[:ru:{d[4]}]]'
    else:
        d[5] = ''

totalsubpage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ կարճ հոդվածներ')
totalsubpage.text = total + helpers.matrix_to_wikitable(data)
totalsubpage.save(summary='թարմացում', botflag=False)
