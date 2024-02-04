import pywikibot as pw
import datetime
import re

commons = pw.Site('commons', 'commons')
hywiki = pw.Site('hy', 'wikipedia')
hywwiki = pw.Site('hyw', 'wikipedia')

today = datetime.date.today()
for i in range(1, 32):
    year = str(today.year)
    month = str(today.month)
    day = str(i)
    if today.month < 10:
        month = '0' + month
    if i < 10:
        day = '0' + day
    title = 'Template:Potd/' + year + '-' + month + '-' + day
    template_in_commons = pw.Page(commons, title)
    if template_in_commons.exists():
        file = re.sub(r'^[^|]+\|([^|]+)[\s\S]+$', r'\1', template_in_commons.text)
        template_in_hy = pw.Page(hywiki, title)
        if not template_in_hy.exists():
            template_in_hy.text = file + '<noinclude>[[Կատեգորիա:Կաղապարներ:Օրվա պատկեր]]</noinclude>'
            template_in_hy.save(summary='Օրվա պատկերը Վիքիպահեստից')
        template_in_hyw = pw.Page(hywwiki, title)
        if not template_in_hyw.exists():
            template_in_hyw.text = file
            template_in_hyw.save(summary='Օրուան Պատկերը Ուիքիպահեստից')
