import pywikibot as pw

import helpers

site = pw.Site('hy', 'wikipedia')
category = pw.Category(site,'Կատեգորիա:Կատեգորիաներ կատեգորիաների համար')

data = []

for cat in category.members(namespaces=[14]):
    cat: pw.Category
    pages_num = int(cat.categoryinfo['pages'])
    if pages_num > 0:
        data.append([pages_num, f'[[:Կատեգորիա:{cat.title(with_ns=False)}|{cat.title(with_ns=False)}]]'])

data.sort(reverse=True)

data = [['Էջերի քանակ', 'Կատեգորիա']] + data

page = pw.Page(site, 'Վիքիպեդիա:Ցանկեր/կատեգորիաներ կատեգորիաների համար')
page.text = helpers.matrix_to_wikitable(data)
page.save('թարմացում', botflag=False)