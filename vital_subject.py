# -*- coding: utf-8 -*-
from pywikibot import pagegenerators as pg
import requests

from helpers import *

UN_SOURCE = 'Անաղբյուր և լրացուցիչ աղբյուրների կարիք ունեցող հոդվածներ'

hywiki = pw.Site('hy', 'wikipedia')


def missing_articles(from_lang, to_lang, category_title, skip_size):
    from_wiki = pw.Site(from_lang, 'wikipedia')
    to_wiki = pw.Site(to_lang, 'wikipedia')

    text = '== [[:' + from_lang + ':Category:' + category_title + ']] == \n'
    if skip_size:
        data = [['Անգլերեն հոդված', 'Հայերեն հոդված', 'Անաղբյուր (hy)', 'մլ N']]
    else:
        data = [['Անգլերեն հոդված', 'en չափ', 'Հայերեն հոդված', 'hy չափ', 'Անաղբյուր (hy)', 'մլ N']]

    category = pw.Category(from_wiki, category_title)
    gen = pg.CategorizedPageGenerator(category, namespaces=[1])

    for talk_page in gen:
        page = talk_page.toggleTalkPage()
        if not page or not page.exists():
            continue
        to_page, item = convert_to(page, to_wiki)
        to_title = '[[' + to_page.title() + ']]' if to_page else ''
        is_unsourced = 'այո' if contains_category(to_page, UN_SOURCE) else ''

        iwN = len(item.sitelinks) if item else 1
        if skip_size:
            data.append([str(page).replace('[[', '[[:'), to_title, is_unsourced, iwN])
        else:
            page_size = page.latest_revision.size
            to_page_size = to_page.latest_revision.size if to_page else None
            data.append([str(page).replace('[[', '[[:'), page_size, to_title, to_page_size, is_unsourced, iwN])
    return text + matrix_to_wikitable(data)


def run(fromwiki, towiki, cats, save_to_page, skip_size=False):
    try:
        savepage = pw.Page(pw.Site(towiki, 'wikipedia'), save_to_page)
        text = ''
        for cat in cats:
            text += '\n' + missing_articles(fromwiki, towiki, cat, skip_size=skip_size)
        savepage.text = text
        savepage.save(summary='թարմացում')
    except Exception as ex:
        pass


settingsJsonURL = "https://hy.wikipedia.org/w/index.php?title=Մասնակից:ԱշոտՏՆՂ/vital-subjects.json&action=raw&ctype=text/json"
settings_page = requests.get(settingsJsonURL).json()
for key in settings_page:
    value = settings_page[key]
    if not value['is_enabled']:
        continue
    run(value['from'], value['to'], value['categories'], key, value['skip_size'])
