import toolforge
import pywikibot as pw

from helpers import convert_to

hywiki = pw.Site('hy', 'wikipedia')
ruwiki = pw.Site('ru', 'wikipedia')
enwiki = pw.Site('en', 'wikipedia')

query = '''SELECT page_title, page_len
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
LIMIT 10000;'''

en = '{| class="wikitable sortable"\n!Հայերեն հոդված!!hy չափ!!Անգլերեն հոդված!!en չափ\n'
ru = '{| class="wikitable sortable"\n!Հայերեն հոդված!!hy չափ!!Ռուսերեն հոդված!!ru չափ\n'
total = 'Ցակից հեռացվել են «Նյութեր տեղանունների բառարանից» և «Ազգանուններ այբբենական կարգով» կատեգորիաների հոդվածները։ Նաև Բազմիմաստություն, Տարվա նավարկում, և Գիրք:ՀՀՖՕՀՏԲ կաղապարն ունեցող հոդվածները։\n'
total += '{| class="wikitable sortable"\n!Հոդված!!Չափ\n'

conn = toolforge.connect('hywiki')
with conn.cursor() as cur:
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        total += '|-\n|[[' + str(r[0].decode('utf-8')) + ']]||' + str(r[1]) + '\n'
        hypage = pw.Page(hywiki, r[0].decode('utf-8'))
        enpage, _ = convert_to(hypage, enwiki)
        if enpage and '<ref' in enpage.text and enpage.latest_revision.size > hypage.latest_revision.size:
            en += '|-\n|' + str(hypage) + '||' + str(r[1]) + '||' + str(enpage) + '||' + str(enpage.latest_revision.size) + '\n'

        rupage, _ = convert_to(hypage, ruwiki)
        if rupage and '<ref' in rupage.text and rupage.latest_revision.size > hypage.latest_revision.size:
            ru += '|-\n|' + str(hypage) + '||' + str(r[1]) + '||' + str(rupage) + '||' + str(rupage.latest_revision.size) + '\n'

en += '|}'
ru += '|}'
total += '|}'

totalsubpage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ կարճ հոդվածներ')
totalsubpage.text = total
totalsubpage.save(summary='թարմացում', botflag=False)
ensubpage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ կարճ հոդվածներ/en')
ensubpage.text = en
ensubpage.save(summary='թարմացում', botflag=False)
rusubpage = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/շատ կարճ հոդվածներ/ru')
rusubpage.text = ru
rusubpage.save(summary='թարմացում', botflag=False)
