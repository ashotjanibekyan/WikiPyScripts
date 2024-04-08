import re

import pywikibot as pw
from pywikibot import pagegenerators as pg

site = pw.Site('hy', 'wikipedia')

cat = pw.Category(site, 'Կատեգորիա:Տառասխալով վերահղումներ')


def replace(w, r):
    pages = pg.SearchPageGenerator(site=site, query=f'insource:/{w}/', namespaces=[0])
    for page in pages:
        if page.title() == w or page.title() == r:
            continue
        page.text = re.sub(w, r, page.text)
        page.save(f'-{w}, +{r}')


for page in cat.members(namespaces=[0]):
    if page.isRedirectPage():
        target = page.getRedirectTarget()
        wrong_name = page.title()
        right_name = target.title()
        replace(wrong_name, right_name)
