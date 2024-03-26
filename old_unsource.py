import pywikibot as pw
import mwparserfromhell as mwp
from datetime import datetime
from dateutil import parser

hywiki = pw.Site('hy', 'wikipedia')
cat = pw.Category(hywiki, 'Կատեգորիա:Նոր_անաղբյուր_հոդվածներ')
delete_template = '{{արագ|անաղբյուր, ժամկետն անցել է։ Կաղապարը փոխարինվել է ԱշբոտՏՆՂ բոտի կողմից, խնդրում ենք համոզվել, որ այս ընթացքում աղբյուր չի ավելացվել}}\n'
for article in list(cat.articles()):
    parsed = mwp.parse(article.text)
    arg = None
    temp = None
    for t in parsed.filter_templates():
        if t.name.matches('Անաղբյուր էջ') and t.has(1):
            arg = str(t.get(1))
            temp = t
            break
    if not arg or not temp:
        continue
    arg = arg.replace(',', '.')
    arg = arg.replace('-', '.')
    parsed_date = parser.parse(arg, dayfirst=True)

    if parsed_date:
        d1 = parsed_date
        d2 = datetime.today()
        delta = d2 - d1
        if delta.days > 7:
            parsed.remove(temp)
            article.text = delete_template + str(parsed).strip()
            article.save(
                summary='-' + str(temp) + ', + {{արագ}}')
