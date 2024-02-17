from typing import Tuple, Optional

import pywikibot
import pywikibot as pw
import pywikibot.data.api as api
import mwparserfromhell as mwp

nsMap = {
    0: "",
    1: "Քննարկում",
    2: "Մասնակից",
    3: "Մասնակցի քննարկում",
    4: "Վիքիպեդիա",
    5: "Վիքիպեդիայի քննարկում",
    6: "Պատկեր",
    7: "Պատկերի քննարկում",
    8: "MediaWiki",
    9: "MediaWiki քննարկում",
    10: "Կաղապար",
    11: "Կաղապարի քննարկում",
    12: "Օգնություն",
    13: "Օգնության քննարկում",
    14: "Կատեգորիա",
    15: "Կատեգորիայի քննարկում",
    100: "Պորտալ",
    101: "Պորտալի քննարկում",
    102: "Վիքինախագիծ",
    103: "Վիքինախագծի քննարկում",
    118: "Սևագիր",
    119: "Սևագրի քննարկում",
    828: "Մոդուլ",
    829: "Մոդուլի քննարկում",
    2300: "Gadget",
    2301: "Gadget talk",
    2302: "Gadget definition",
    2303: "Gadget definition talk",
    -2: "Մեդիա",
    -1: "Սպասարկող"
}

item_cache = {}


def convert_to_many(from_wiki: pywikibot.Site, pages, to_wiki_code, include_count=False):
    titles = '|'.join([p.title() if isinstance(p, pw.Page) else p for p in pages])
    params = {'action': 'query',
              'prop': 'langlinks',
              'formatversion': '2',
              'lllimit': 'max',
              'titles': titles}
    if not include_count:
        params['lllang'] = to_wiki_code
    should_continue = True
    data = {}
    count = {}
    while should_continue:
        req = api.Request(site=from_wiki, parameters=params)
        r = req.submit()
        for p in r['query']['pages']:
            title = p['title']
            if 'langlinks' in p:
                langlinks = p['langlinks']
                if title not in data or not data[title]:
                    data[title] = None
                    for lang in langlinks:
                        if lang['lang'] == to_wiki_code:
                            data[title] = lang['title']
                if title not in count:
                    count[title] = len(langlinks) + 1
                else:
                    count[title] += len(langlinks)
            elif title not in data:
                data[title] = None
                count[title] = 1
        if 'continue' in r and 'llcontinue' in r['continue']:
            params['llcontinue'] = r['continue']['llcontinue']
        else:
            should_continue = False
    result = []
    for key, value in data.items():
        if include_count:
            result.append((key, value, count[key]))
        else:
            result.append((key, value))
    return result


def convert_to(from_page: pywikibot.Page, to_wiki: pywikibot.Site) -> Tuple[
    Optional[pywikibot.Page], pywikibot.ItemPage]:
    if from_page.title(with_ns=True) in item_cache:
        item = item_cache[from_page.title(with_ns=True)]
    else:
        item = pywikibot.ItemPage.fromPage(from_page, lazy_load=True)
        item_cache[from_page.title(with_ns=True)] = item
    if not item or not item.exists():
        return None, item
    to_link = item.sitelinks.get(to_wiki.code + 'wiki')
    if to_link:
        return pw.Page(to_wiki, to_link.title, ns=to_link.namespace), item
    return None, item


def contains_category_many(wiki: pywikibot.Site, pages, category):
    titles = '|'.join([p.title() if isinstance(p, pw.Page) else p for p in pages])
    params = {'action': 'query',
              'prop': 'categories',
              'formatversion': '2',
              'cllimit': 'max',
              'clcategories': category,
              'titles': titles}
    should_continue = True
    data = {}
    while should_continue:
        req = api.Request(site=wiki, parameters=params)
        r = req.submit()
        for p in r['query']['pages']:
            data[p['title']] = 'categories' in p
        if 'continue' in r and 'clcontinue' in r['continue']:
            params['clcontinue'] = r['continue']['clcontinue']
        else:
            should_continue = False
    return data


def get_size_many(wiki: pw.Site, pages):
    chunk_size = 50
    data = {}
    if wiki.code + '.' + str(wiki.family) in ('hy.wikipedia', 'hy.wiktionary', 'hyw.wikipedia', 'wikidata.wikidata'):
        chunk_size = 500
    for i in range(0, len(pages), chunk_size):
        chunk = pages[i:i + chunk_size]
        titles = '|'.join([p.title() if isinstance(p, pw.Page) else p for p in chunk])
        params = {'action': 'query',
                  'prop': 'info',
                  'formatversion': '2',
                  'titles': titles}
        should_continue = True
        while should_continue:
            req = api.Request(site=wiki, parameters=params)
            r = req.submit()
            for p in r['query']['pages']:
                data[p['title']] = p['length'] if 'length' in p else 0
            if 'continue' in r and 'incontinue' in r['continue']:
                params['incontinue'] = r['continue']['incontinue']
            else:
                should_continue = False
    return data


def contains_category(page: pywikibot.Page, category_title: str) -> bool:
    if not page or not page.exists():
        return False

    for category in page.categories():
        if category.title(with_ns=False) == category_title:
            return True

    return False


def matrix_to_wikitable(matrix):
    text = '{| class="wikitable sortable"\n'
    text += '!' + '!!'.join(matrix[0]) + '\n'
    for i in range(1, len(matrix)):
        if isinstance(matrix[i], list) and len(matrix[i]) == len(matrix[0]):
            row = (str(x) if x or x == 0 else ' ' for x in matrix[i])
            text += '|-\n|' + '||'.join(row) + '\n'
    text += '|}'
    return text


def without_comments(wiki_text):
    if wiki_text is None:
        return None
    wikicode = mwp.parse(wiki_text)
    for node in wikicode.nodes[:]:
        if isinstance(node, mwp.nodes.Comment):
            wikicode.remove(node)
    return str(wikicode).strip()


def get_first_param(wiki_text):
    templates = mwp.parse(wiki_text).filter_templates()
    if templates:
        if templates[0].has(1):
            first_param_value = templates[0].get(1).value
            return str(first_param_value).strip()
    return None


def round_100(i):
    return round(i / 100.0) * 100


def get_wikipedias(*args):
    result = []
    for arg in args:
        result.append(pw.Site(arg, 'wikipedia'))
    return result


def get_cell_txt(cell):
    if not cell:
        return ''
    if isinstance(cell, bytes):
        return str(cell.decode('utf-8')).replace('_', ' ')
    else:
        return str(cell).replace('_', ' ')
