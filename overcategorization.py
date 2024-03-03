import json

import pywikibot as pw

site = pw.Site('hy', 'wikipedia')

data = json.loads(pw.Page(site, 'Մասնակից:ԱշոտՏՆՂ/գերկատեգորիզացիա.json').text)


def check_cat(cat, cats_to_delete):
    for cat_to_delete in cats_to_delete:
        c = pw.Category(site, "Category:" + cat_to_delete)
        for page in c.members(namespaces=[0]):
            if cat not in [p.title(with_ns=False) for p in page.categories()]:
                continue
            page.change_category(
                c,
                None,
                f'-[[Կատեգորիա:{cat_to_delete}]], քանի որ արդեն կա [[Կատեգորիա:{cat}]], ([[Մասնակից:ԱշոտՏՆՂ/գերկատեգորիզացիա.json|ուղղել բոտին]])')


for k, val in data.items():
    check_cat(k, val)
