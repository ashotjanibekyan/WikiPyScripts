import toolforge
import pywikibot as pw

import helpers

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

query = '''SELECT concat('Սևագիր:', page_title) AS Title
FROM revision
JOIN page ON rev_page = page_id
AND page_latest = rev_id
WHERE page_namespace = 118
  AND (rev_timestamp < DATE_ADD(NOW(), INTERVAL -6 MONTH))
ORDER BY rev_timestamp'''

with conn.cursor() as cur:
    text = 'Սևագրում վերջին վեց ամսվա ընթացքում փոփոխություն չի արվել։ Վերականգնելու համար խնդրում ենք դիմել [[Վիքիպեդիա:Ադմինիստրատորների տեղեկատախտակ|Ադմինիստրատորների տեղեկատախտակ]]'
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        page = pw.Page(hywiki, helpers.get_cell_txt(r[0]))
        if page.exists():
            page.delete(reason=text, prompt=False)
        talk = page.toggleTalkPage()
        if talk.exists():
            talk.delete(reason=text, prompt=False)
