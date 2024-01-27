from typing import Tuple, Optional

import pywikibot
import pywikibot as pw


def convert_to(from_page: pywikibot.Page, to_wiki: pywikibot.Site) -> Tuple[Optional[pywikibot.Page], pywikibot.ItemPage]:
    item = pywikibot.ItemPage.fromPage(from_page, lazy_load=True)
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
            row = (str(x) if x else ' ' for x in matrix[i])
            text += '|-\n|' + '||'.join(row) + '\n'
    text += '|}'
    return text


def round_100(i):
    return round(i / 100.0) * 100
