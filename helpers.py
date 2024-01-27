import pywikibot
import pywikibot as pw


def convert_to(from_page, to_wiki):
    item = pywikibot.ItemPage.fromPage(from_page, lazy_load=True)
    if not item or not item.exists():
        return None
    to_link = item.sitelinks.get(to_wiki.code + 'wiki')
    if to_link:
        return pw.Page(to_wiki, to_link.title)


def matrix_to_wikitable(self, matrix):
    text = '{| class="wikitable sortable"\n'
    text += '!' + '!!'.join(matrix[0]) + '\n'
    for i in range(1, len(matrix)):
        if isinstance(matrix[i], list) and len(matrix[i]) == len(matrix[0]):
            row = (str(x) if x else ' ' for x in matrix[i])
            text += '|-\n|' + '||'.join(row) + '\n'
    text += '|}'
    return text
