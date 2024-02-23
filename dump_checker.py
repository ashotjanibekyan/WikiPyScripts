import re
import sys

import pywikibot as pw
import mwparserfromhell as mwp
from pywikibot import xmlreader
import concurrent.futures

from tqdm import tqdm

hywiki = pw.Site('hy', 'wikipedia')


def get_duplicates(my_list):
    unique_values = set()
    result = []

    for item in my_list:
        if item not in unique_values:
            unique_values.add(item)
        else:
            result.append(item)
    return result


def headings(parsed, parent, level):
    sections = parsed.get_sections(include_headings=True, levels=[level])
    result = [parent] if parent else []
    for section in sections:
        heading = str(section.filter_headings()[0].title).strip()
        i = 1
        sub = headings(section, heading, level + i)
        while len(sub) < 2 and i < 7:
            i += 1
            sub = headings(section, heading, level + i)
        for s in sub:
            if parent:
                result.append(parent + " > " + s)
            else:
                result.append(s)
    return result


def duplicate_external(page):
    try:
        matches = re.findall(r'\{\{ *([Աա]րտաքին հղումներ|[Աա]Հ|[Aa]uthority control) *}}', page.text)
        if len(matches) <= 1:
            return ''
        else:
            return f'# [[{page.title}]]\n'
    except Exception as e:
        print(e)
        return ''


def process_page(page):
    try:
        parsed = mwp.parse(page.text)
        r = headings(parsed, '', 2)
        duplicates = get_duplicates(r)
        if duplicates:
            duplicates = list(map(lambda x: f'"{x}"', duplicates))
            return f'# [[{page.title}]] - {", ".join(duplicates)}\n'
        else:
            return ''
    except Exception as e:
        print(e)
        return ''


def main_from_dump(func, mult):
    reader = xmlreader.XmlDump('/public/dumps/public/hywiki/latest/hywiki-latest-pages-meta-current.xml.bz2')
    read = reader.parse()
    results = []
    if mult:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [result for result in executor.map(func, read, chunksize=5000) if result]
    else:
        for page in read:
            result = func(page)
            if result:
                results.append(result)
    return ''.join(results)


def remove_done(func, page_title):
    class XmlEntryMock:
        def __init__(self, title, text):
            self.title = title
            self.text = text

    p = pw.Page(hywiki, page_title)
    results = []
    linked_pages = list(p.linkedPages())
    for page in linked_pages:
        results.append(func(XmlEntryMock(text=page.text, title=page.title())))
    return ''.join(results)


if __name__ == '__main__':
    page_title = None
    method = None
    is_clean = len(sys.argv) >= 2 and sys.argv[2] == 'clean'
    multi = len(sys.argv) >= 3 and sys.argv[3] == 'multi'
    if sys.argv[1] == 'sections':
        page_title = 'Վիքիպեդիա:Ցանկեր/կրկնվող բաժիններով հոդվածներ'
        method = process_page
    elif sys.argv[1] == 'externallinks':
        page_title = "Վիքիպեդիա:Ցանկեր/կրկնվող արտաքին հղում"
        method = duplicate_external

    if page_title and method:
        p = pw.Page(hywiki, page_title)
        p.text = remove_done(method, page_title) if is_clean else main_from_dump(method, multi)
        p.save('մաքրում' if is_clean else 'թարմացում')
