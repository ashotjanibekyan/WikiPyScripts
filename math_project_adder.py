import re
import toolforge
import pywikibot as pw

import helpers

enwiki = pw.Site('en', 'wikipedia')
hywiki = pw.Site('hy', 'wikipedia')

enconn = toolforge.connect('enwiki')
hyconn = toolforge.connect('hywiki')

en_query = '''WITH MathTitle AS
  (SELECT page_title
   FROM page
   JOIN categorylinks ON cl_from = page_id
   WHERE cl_to in ('High-priority_mathematics_articles',
                   'Low-priority_mathematics_articles',
                   'Mid-priority_mathematics_articles',
                   'NA-priority_mathematics_articles',
                   'Top-priority_mathematics_articles',
                   'Unknown-priority_mathematics_articles')
   LIMIT 30000)
SELECT DISTINCT ll_title,
                p1.page_title
FROM page p1
JOIN langlinks ON ll_from = p1.page_id
WHERE page_namespace = 0
  AND ll_lang = 'hy'
  AND EXISTS
    (SELECT 1
     FROM MathTitle
     WHERE p1.page_title = page_title);'''

hy_query = '''SELECT page_title
FROM page
JOIN categorylinks ON cl_from = page_id
WHERE cl_to = 'Մաթեմատիկական_հոդվածներ'
LIMIT 30000;'''

fields = {
    'algebra': 'հանրահաշիվ',
    'analysis': 'անալիզ',
    'applied': 'կիրառական',
    'applied mathematics': 'կիրառական',
    'basics': 'տարրական',
    'discrete': 'դիսկրետ',
    'discrete mathematics': 'դիսկրետ',
    'foundations': 'հիմքեր',
    'foundations, logic, and set theory': 'հիմքեր, տրամաբանություն և բազմությունների տեսություն',
    'logic': 'բազմությունների տեսություն',
    'set theory': 'տրամաբանություն',
    'general': 'ընդհանուր',
    'geometry': 'երկրաչափություն',
    'history': 'պատմություն',
    'mathematical physics': 'ֆիզիկա',
    'mathematician': 'մաթեմատիկոս',
    'mathematicians': 'մաթեմատիկոս',
    'number theory': 'թվերի տեսություն',
    'probability': 'հավանականություն',
    'probability and statistics': 'հավանականություն և վիճակագրություն',
    'statistics': 'վիճակագրություն',
    'topology': 'տոպոլոգիա'
}

priorities = {
    'top': 'բարձրագույն',
    'high': 'բարձր',
    'mid': 'միջին',
    'low': 'ցածր'
}


def create_hy_template(text):
    templates = r'(Maths rating|Math rating|Maths rating small|Mathrating|WikiProject Maths|WikiProject Math|WP Maths|WPMath|WikiProject Mathematics rating|WPMATHEMATICS)'
    m = re.search(r'(\{\{' + templates + r'[^}]+\}\})', text, re.IGNORECASE)
    if m:
        template = m.group(0).replace('\n', '')

        priority_reg = r'\{\{' + templates + r'.*\| *priority *= *([^|}]+).*\}\}'
        priority = re.sub(priority_reg, r'\2', template, flags=re.IGNORECASE)
        if priority == template:
            priority = ''

        field_reg = r'\{\{' + templates + r'.*\| *field *= *([^|}]+).*\}\}'
        field = re.sub(field_reg, r'\2', template, flags=re.IGNORECASE)
        if field == template:
            field = ''

        vital_reg = r'\{\{' + templates + r'.*\| *vital *= *([^|}]+).*\}\}'
        vital = re.sub(vital_reg, r'\2', template, flags=re.IGNORECASE)
        if vital == template:
            vital = ''

        importance_reg = r'\{\{' + templates + r'.*\| *importance *= *([^|}]+).*\}\}'
        importance = re.sub(importance_reg, r'\2', template, flags=re.IGNORECASE)
        if importance == template:
            importance = ''

        fieldhy = ''
        if field.lower().strip() in fields:
            fieldhy = ' | բնագավառ = ' + fields[field.lower().strip()]

        priorityhy = ''
        if importance.lower().strip() in priorities:
            priorityhy = ' | կարևորություն = ' + priorities[importance.lower().strip()]

        if priority.lower().strip() in priorities:
            priorityhy = ' | կարևորություն = ' + priorities[priority.lower().strip()]

        vitalhy = ''
        if vital:
            vitalhy = ' | կարևորագույն = ' + 'այո'

        hytemplate = '{{Վիքինախագիծ Մաթեմատիկա' + fieldhy + priorityhy + vitalhy + '}}'
        return hytemplate
    return None

hy_en_map = {}
with enconn.cursor() as cur:
  cur.execute(en_query)
  results = cur.fetchall()
  for r in results:
    hy_title = helpers.get_cell_txt(r[0])
    en_title = helpers.get_cell_txt(r[1])
    hy_en_map[hy_title] = en_title

already_has = set()
with hyconn.cursor() as cur:
  cur.execute(hy_query)
  results = cur.fetchall()
  for r in results:
    already_has.add(helpers.get_cell_txt(r[0]))

for hy_title in hy_en_map:
  if hy_title not in already_has:
    hy_page = pw.Page(hywiki, hy_title)
    en_talk_page = pw.Page(enwiki, 'Talk:' + hy_en_map[hy_title])
    if not en_talk_page or not en_talk_page.exists():
      continue
    hy_template = create_hy_template(en_talk_page.text)
    if not hy_template:
      continue
    hy_page_talk = hy_page.toggleTalkPage()
    hy_page_talk.text = re.sub(r'\{\{Վիքինախագիծ Մաթեմատիկա}}\n?', '', hy_page_talk.text)
    if '{{Վիքինախագիծ Մաթեմատիկա' not in hy_page_talk.text:
        hy_page_talk.text = hy_template + '\n' + hy_page_talk.text
        hy_page_talk.save(
            summary='+' + hy_template + ', ըստ [[Special:PermaLink/7367323#{{Վիքինախագիծ_Մաթեմատիկա}}_կաղապարը_քննարկման_էջերում]]')

watchlist = pw.Page(hywiki, 'Վիքինախագիծ:Մաթեմատիկա/Հոդվածներ')
cat = pw.Category(hywiki, 'Կատեգորիա:Մաթեմատիկական հոդվածներ')
watchlist.text = ''
for talk in cat.members():
    page = talk.toggleTalkPage()
    if page.namespace() == 0:
        watchlist.text += f'[[{page.title()}]]-[[{talk.title()}]] '
watchlist.save('թարմացում')