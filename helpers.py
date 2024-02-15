from typing import Tuple, Optional

import pywikibot
import pywikibot as pw
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
        return pw.Page(to_wiki, to_link.title), item
    return None, item


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