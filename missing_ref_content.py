import re
import pywikibot as pw
import mwparserfromhell as mwp

import helpers
from helpers import convert_to

hywiki, ruwiki, enwiki = helpers.get_wikipedias('hy', 'ru', 'en')

page1 = pw.Page(hywiki, 'Ամառային օլիմպիական խաղեր 2020')


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


def get_reference_with_content_by_name(page_text, ref_name):
    parsed = mwp.parse(page_text)
    for tag in parsed.filter_tags():
        if tag.has('name') and str(tag.get('name').value) == ref_name and not tag.self_closing:
            return tag
    return None


def process_page(page):
    text = page.text
    missing_refs = extract_references_without_content(text)
    enpage, item = convert_to(page, enwiki)

    new_refs = {}

    for ref_name in missing_refs:
        if enpage:
            from_en = get_reference_with_content_by_name(enpage.text, ref_name)
            if from_en:
                new_refs[ref_name] = from_en
                continue

        rupage, item = convert_to(page, ruwiki)
        if rupage:
            from_ru = get_reference_with_content_by_name(rupage.text, ref_name)
            if from_ru:
                new_refs[ref_name] = from_ru

    for new_ref in new_refs:
        text = re.sub(r'<ref *name *="?' + new_ref + r'"? */>', str(new_refs[new_ref]), text, count=1)

    if text != page.text:
        page.text = text
        page.save(' ')


cat = pw.Category(hywiki, 'Կատեգորիա:Դատարկ ծանոթագրություններով հոդվածներ')

for member in cat.members():
    process_page(member)
