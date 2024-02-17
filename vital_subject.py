# -*- coding: utf-8 -*-
from pywikibot import pagegenerators as pg
import requests

import helpers
from helpers import *

UN_SOURCE = 'Կատեգորիա:Անաղբյուր և լրացուցիչ աղբյուրների կարիք ունեցող հոդվածներ'

hywiki = pw.Site('hy', 'wikipedia')


def missing_articles(from_lang, to_lang, category_title, skip_size):
    from_wiki = pw.Site(from_lang, 'wikipedia')
    to_wiki = pw.Site(to_lang, 'wikipedia')

    text = '== [[:' + from_lang + ':Category:' + category_title + ']] == \n'
    if skip_size:
        data = [['Անգլերեն հոդված', 'Հայերեն հոդված', 'Անաղբյուր (hy)', 'մլ N']]
    else:
        data = [['Անգլերեն հոդված', 'en չափ', 'Հայերեն հոդված', 'hy չափ', 'Անաղբյուր (hy)', 'մլ N']]

    pages = list([p.toggleTalkPage() for p in list(pw.Category(from_wiki, category_title).members(namespaces=[1]))])
    lang_link_data = []

    for i in range(0, len(pages), 50):
        chunk = pages[i:i + 50]
        lang_link_data += helpers.convert_to_many(from_wiki, chunk, to_lang, include_count=True)
    to_titles = list(filter(lambda x: x, map(lambda x: x[1], lang_link_data)))
    unsourced_map = {}
    for i in range(0, len(to_titles), 500):
        chunk = to_titles[i:i + 500]
        unsourced_map.update(helpers.contains_category_many(wiki=to_wiki,
                                                            pages=chunk,
                                                            category=UN_SOURCE))
    from_sizes = {}
    to_sizes = {}
    if not skip_size:
        from_sizes = helpers.get_size_many(from_wiki, pages)
        to_sizes = helpers.get_size_many(from_wiki, to_titles)
    lang_link_data.sort()
    for lang_link in lang_link_data:
        to_title = lang_link[1]
        to_link = '[[' + to_title + ']]' if to_title else ''
        from_title = lang_link[0]
        from_link = f'[[:{from_lang}:{from_title}]]'
        is_unsourced = 'այո' if to_title in unsourced_map and unsourced_map[to_title] else ''
        iwN = lang_link[2]
        if skip_size:
           data.append([from_link, to_link, is_unsourced, iwN])
        else:
           page_size = helpers.round_100(from_sizes[from_title]) if from_title and from_title in from_sizes else ''
           to_page_size = helpers.round_100(to_sizes[to_title]) if to_title and to_title in to_sizes else ''
           data.append([from_link, page_size, to_link, to_page_size, is_unsourced, iwN])
    return text + matrix_to_wikitable(data)


def run(fromwiki, towiki, cats, save_to_page, skip_size=False):
    try:
        savepage = pw.Page(pw.Site(towiki, 'wikipedia'), save_to_page)
        text = ''
        for cat in cats:
            text += '\n' + missing_articles(fromwiki, towiki, cat, skip_size=skip_size)
        savepage.text = text
        savepage.save(summary='թարմացում', botflag=False)
    except Exception as ex:
        pass


settingsJsonURL = "https://hy.wikipedia.org/w/index.php?title=Մասնակից:ԱշոտՏՆՂ/vital-subjects.json&action=raw&ctype=text/json"
settings_page = requests.get(settingsJsonURL).json()
for key in settings_page:
    value = settings_page[key]
    if not value['is_enabled']:
        continue
    run(value['from'], value['to'], value['categories'], key, value['skip_size'])
