import pywikibot as pw
import re
from datetime import datetime

hywiki = pw.Site('hy', 'wikipedia')
cat = pw.Category(hywiki, 'Կատեգորիա:Նոր_անաղբյուր_հոդվածներ')
for article in list(cat.articles()):
    m = re.search(r'Անաղբյուր էջ\|(\d+),(\d+),(\d+)', article.text)
    if m:
        d1 = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        d2 = datetime.today()
        delta = d2 - d1
        if delta.days > 7:
            article.text = re.sub(r'\{\{Անաղբյուր էջ\|(\d+),(\d+),(\d+)\}\}',
                                  '{{արագ|անաղբյուր, ժամկետն անցել է։ Կաղապարը փոխարինվել է ԱշբոտՏՆՂ բոտի կողմից, խնդրում ենք համոզվել, որ այս ընթացքում աղբյուր չի ավելացվել}}',
                                  article.text)
            article.save(
                summary='-{{ԱՆաղբյուր էջ|' + m.group(1) + ',' + m.group(2) + ',' + m.group(3) + '}}, + {{արագ}}')
