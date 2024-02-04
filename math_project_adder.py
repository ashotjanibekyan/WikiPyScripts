import pywikibot as pw
import re

from helpers import convert_to

hywiki = pw.Site('hy', 'wikipedia')
enwiki = pw.Site('en', 'wikipedia')

temp = pw.Page(enwiki, 'Template:WikiProject Mathematics')
gen = temp.getReferences(only_template_inclusion=True, namespaces=1, follow_redirects=True)

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


for p in gen:
    skipped = False
    en_page = p.toggleTalkPage()
    hy_page, _ = convert_to(en_page, hywiki)
    if hy_page:
        hy_template = create_hy_template(p.text)
        if not hy_template:
            skipped = True
            continue
        hy_page_talk = hy_page.toggleTalkPage()
        hy_page_talk.text = re.sub(r'\{\{Վիքինախագիծ Մաթեմատիկա}}\n?', '', hy_page_talk.text)
        if '{{Վիքինախագիծ Մաթեմատիկա' not in hy_page_talk.text:
            hy_page_talk.text = hy_template + '\n' + hy_page_talk.text
            hy_page_talk.save(
                summary='+' + hy_template + ', ըստ [[Special:PermaLink/7367323#{{Վիքինախագիծ_Մաթեմատիկա}}_կաղապարը_քննարկման_էջերում]]')
        else:
            skipped = True
