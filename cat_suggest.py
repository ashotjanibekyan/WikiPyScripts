from typing import List

import pywikibot as pw
import pywikibot.data.api as api
import re
import random

import requests

import helpers


def get_cats(pages: List[str], wiki):
    titles = '|'.join([p for p in pages])
    params = {'action': 'query',
              'prop': 'categories',
              'titles': titles,
              'formatversion': 2,
              'clshow': '!hidden',
              'cllimit': 'max'}

    should_continue = True
    data = {}
    while should_continue:
        req = api.Request(site=wiki, parameters=params)
        r = req.submit()
        for p in r['query']['pages']:
            if 'categories' not in p:
                continue
            if p['title'] not in data:
                data[p['title']] = []
            data[p['title']] += list(map(lambda x: x['title'], p['categories']))
        if 'continue' in r and 'clcontinue' in r['continue']:
            params['clcontinue'] = r['continue']['clcontinue']
        else:
            should_continue = False
    result = []
    for key, value in data.items():
        result.append({
            'title': key,
            'categories': value
        })
    return result


def get_random_articles_from_cat(cat: pw.Category, rec=0, count=1000) -> List[pw.Page]:
    members = list(cat.members(recurse=rec, namespaces=0))

    if count >= len(members):
        return members

    return random.sample(members, count)


def list_to_freq(dic, l):
    for obj in l:
        if obj in dic:
            dic[obj] += 1
        else:
            dic[obj] = 1


def skip_page_to_dic(page: pw.Page):
    dic = {}
    if page.exists():
        lines = page.text.splitlines()
        for line in lines:
            if len(line) > 0 and line[0] == '*':
                line = re.sub(r'^\* *(.+) *\n?', r'\1', line)
                line = line.replace('_', ' ')
                dic[line] = True
    return dic


def find_freqs(target_wiki_articles: List[pw.Page], source_wiki: pw.Site, target_wiki: pw.Site, save_to_title: str):
    source_wiki_cat_freq = {}
    target_wiki_cat_freq = {}
    skip_dic = skip_page_to_dic(pw.Page(target_wiki, save_to_title + '/անտեսված հոդվածներ'))
    target_wiki_articles = list(filter(lambda a: a.title() not in skip_dic, target_wiki_articles))
    target_articles = []
    source_articles = []
    for i in range(0, len(target_wiki_articles), 500):
        chunk = target_wiki_articles[i:i + 500]
        chunk_articles_converted = helpers.convert_to_many(target_wiki, chunk, source_wiki.code)
        for a in chunk_articles_converted:
            if not a[0] or not a[1]:
                continue
            target_articles.append(a[0])
            source_articles.append(a[1])

    for i in range(0, len(target_articles), 500):
        chunk = target_articles[i:i + 500]
        chunk_targets_cats = get_cats(chunk, target_wiki)
        for chunk_target_cats in chunk_targets_cats:
            list_to_freq(target_wiki_cat_freq, chunk_target_cats['categories'])

    for i in range(0, len(source_articles), 50):
        chunk = source_articles[i:i + 50]
        chunk_targets_cats = get_cats(chunk, source_wiki)
        for chunk_target_cats in chunk_targets_cats:
            list_to_freq(source_wiki_cat_freq, chunk_target_cats['categories'])
    return source_wiki_cat_freq, target_wiki_cat_freq


def process_raw_freqs(source_freq, target_freq, source_wiki, target_wiki, save_to_title, cutoff):
    source_freq_converted = {}
    skip_dic = skip_page_to_dic(pw.Page(target_wiki, save_to_title + '/անտեսված կատեգորիաներ'))
    source_freq = {key: value for key, value in source_freq.items() if cutoff >= 3 and key not in skip_dic and not key.endswith(' stubs')}

    cat_names = list(source_freq.keys())
    cat_source_to_target = {}
    for i in range(0, len(cat_names), 50):
        chunk = cat_names[i:i + 50]
        chunk_cats_converted = helpers.convert_to_many(source_wiki, chunk, target_wiki.code)
        for a in chunk_cats_converted:
            if not a[0]:
                continue
            cat_source_to_target[a[0]] = a[1]

    for cat_name in source_freq:
        converted = cat_source_to_target[cat_name]
        if converted:
            if converted in target_freq:
                source_freq_converted[converted] = source_freq[cat_name] - target_freq[converted]
            else:
                source_freq_converted[converted] = source_freq[cat_name]
        else:
            source_freq_converted[cat_name] = source_freq[cat_name]
    sorted_freq = sorted([(v, k) for k, v in source_freq_converted.items()], reverse=True)
    res = []
    for count, cat_name in sorted_freq:
        if count >= cutoff:
            res.append((cat_name, count))
    return res


def make_suggestions_cat(cat_name: str,
                         source_wiki: pw.Site,
                         target_wiki: pw.Site,
                         save_to_title: str,
                         sample_size: int,
                         cutoff: int,
                         rec: int):
    TEXT = '''Այս էջում կարող եք գտնել «{}» կատեգորիայի հոդվածներում կատեգորիա ավելացնելու առաջարկներ։ Եթե կարծում եք, որ ինչ-որ հոդված չպետք է հայտնվի այս էջում,․ խնդրում ենք հոդվածի անունը ավելացնել [[{}]] էջում այնտեղ նշված ֆորմատով։ Եթե կարծում եք, որ ինչ-որ կատեգորիա չպետք է հայտնվի այս էջում, խնդրում ենք կատեգորիայի անունը ավելացնել [[{}]] էջում այնտեղ նշված ֆորմատով։\n'''.format(cat_name.replace('_', ' '),
                                                    save_to_title.replace('_', ' ') + '/անտեսված հոդվածներ',
                                                    save_to_title.replace('_', ' ') + '/անտեսված կատեգորիաներ')
    save_to = pw.Page(target_wiki, save_to_title)
    cat = pw.Category(target_wiki, cat_name)
    target_wiki_articles = get_random_articles_from_cat(cat, rec=rec, count=sample_size)
    raw_freqs = find_freqs(target_wiki_articles, source_wiki, target_wiki, save_to_title)
    raw_data = process_raw_freqs(raw_freqs[0], raw_freqs[1], source_wiki, target_wiki, save_to_title, cutoff)
    text = '==' + cat_name + '==\n'
    for item in raw_data:
        if len(text.encode('utf-8')) > 100000:
            break
        if 'Category:' in item[0]:
            text += '\n# [[:en:' + item[0] + ']] - ' + str(item[1])
        elif 'Категория:' in item[0]:
            text += '\n# [[:ru:' + item[0] + ']] - ' + str(item[1])
        elif 'Կատեգորիա:' in item[0]:
            text += '\n# [[:' + item[0] + ']] - ' + str(item[1])
        else:
            text += '\n# ' + item[0] + ' - ' + str(item[1])
    save_to.text = TEXT + text
    save_to.save(summary='թարմացում', botflag=False)


settingsJsonURL = ("https://hy.wikipedia.org/w/index.php?title=Մասնակից:ԱշոտՏՆՂ/missing-categories.json&action=raw"
                   "&ctype=text/json")
settings = requests.get(settingsJsonURL).json()

expection = None
for key in settings:
    s = settings[key]
    try:
        make_suggestions_cat(cat_name=s['target_category'],
                             source_wiki=pw.Site(s['source_wiki'], 'wikipedia'),
                             target_wiki=pw.Site('hy', 'wikipedia'),
                             save_to_title=key,
                             sample_size=s['sample_size'],
                             cutoff=s['cutoff'],
                             rec=s['rec'])
    except Exception as ex:
        expection = ex

if expection:
    raise expection
