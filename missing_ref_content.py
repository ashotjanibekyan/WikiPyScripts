import re
import pywikibot as pw
import mwparserfromhell as mwp

import helpers
from helpers import convert_to

hywiki, ruwiki, enwiki = helpers.get_wikipedias('hy', 'ru', 'en')

filename = "./missing_ref_content_checked.txt"
CHECKED_PAGES = set()

try:
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            CHECKED_PAGES.add(line.strip())
except FileNotFoundError:
    print(f"The file '{filename}' does not exist.")


def extract_references_without_content(page_text):
    parsed = mwp.parse(page_text)

    references_with_content = {}
    missing_refs = []

    for tag in parsed.filter_tags():
        if tag.tag == 'ref' and tag.has('name'):
            ref_name = str(tag.get('name').value)

            if ref_name in references_with_content:
                references_with_content[ref_name].append(tag)
            else:
                references_with_content[ref_name] = [tag]

    for ref_name, ref_tags in references_with_content.items():
        has_content = any(not ref_tag.self_closing for ref_tag in ref_tags)
        if not has_content:
            missing_refs.append(ref_name)

    return missing_refs


parse_map = {}


def get_reference_with_content_by_name(page_text, ref_name):
    parsed = mwp.parse(page_text) if page_text not in parse_map else parse_map[page_text]
    parse_map[page_text] = parsed
    for tag in parsed.filter_tags():
        if tag.has('name') and str(tag.get('name').value) == ref_name and not tag.self_closing:
            return tag
    return None


def get_from_rev(revision, ref_name):
    if 'slots' in revision and 'main' in revision['slots'] and '*' in revision['slots']['main'] and ref_name in \
            revision['slots']['main']['*']:
        from_en = get_reference_with_content_by_name(revision['slots']['main']['*'], ref_name)
        if from_en:
            return (from_en, revision['revid'])
    return (None, None)


def is_power_of_two(num):
    return (num & (num - 1)) == 0 and num > 0


def process_page(page):
    global parse_map
    parse_map = {}
    text = page.text
    missing_refs = extract_references_without_content(text)
    enpage, item = convert_to(page, enwiki)

    new_refs = {}
    en_revs = []
    ru_revs = []

    for ref_name in missing_refs:
        found_on_en_revision = False
        i = 0
        if enpage and enpage.exists():
            for revision in enpage.revisions(content=True, endtime=page.oldest_revision['timestamp'], total=32):
                i += 1
                if not is_power_of_two(i):
                    continue
                if 'slots' in revision and 'main' in revision['slots'] and '*' in revision['slots'][
                    'main'] and ref_name in revision['slots']['main']['*']:
                    from_en = get_reference_with_content_by_name(revision['slots']['main']['*'], ref_name)
                    if from_en:
                        new_refs[ref_name] = from_en
                        en_revs.append(revision['revid'])
                        found_on_en_revision = True
                        break
        if found_on_en_revision:
            continue
        rupage, item = convert_to(page, ruwiki)
        i = 0
        if rupage and rupage.exists():
            for revision in rupage.revisions(content=True, endtime=page.oldest_revision['timestamp'], total=32):
                i += 1
                if not is_power_of_two(i):
                    continue
                if 'slots' in revision and 'main' in revision['slots'] and '*' in revision['slots'][
                    'main'] and ref_name in revision['slots']['main']['*']:
                    from_ru = get_reference_with_content_by_name(revision['slots']['main']['*'], ref_name)
                    if from_ru:
                        new_refs[ref_name] = from_ru
                        ru_revs.append(revision['revid'])
                        break

    for new_ref in new_refs:
        text = re.sub(r'<ref *name *="?' + new_ref + r'"? */>', str(new_refs[new_ref]), text, count=1)

    if text != page.text:
        summary = 'Ծանոթագրություններ ըստ՝ ' + ', '.join(
            map(lambda x: f'[[:en:Special:PermaLink/{str(x)}]]', list(set(en_revs)))) + ', '.join(
            map(lambda x: f'[[:ru:Special:PermaLink/{str(x)}]]', list(set(ru_revs))))
        page.text = text
        page.save(summary)

    with open(filename, 'a', encoding='utf=8') as f:
        f.write(page.title(with_ns=True) + '\n')


cat = pw.Category(hywiki, 'Կատեգորիա:Դատարկ ծանոթագրություններով հոդվածներ')

for member in cat.members(reverse=True):
    if member.title(with_ns=True) not in CHECKED_PAGES:
        process_page(member)
