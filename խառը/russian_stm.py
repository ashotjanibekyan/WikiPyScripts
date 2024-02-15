import re

import pywikibot as pw
from pywikibot import pagegenerators as pg

from helpers import convert_to

hywiki = pw.Site('hy', 'wikipedia')
ruwiki = pw.Site('ru', 'wikipedia')

file1 = open('../titlelist.txt', 'r', encoding='utf-8')
Lines = file1.readlines()

for title in Lines:
    page = pw.Page(hywiki, title)
    if 'wikidata/population' in page.text.lower():
        continue
    hymatch = re.search(r'== *Բնակչությունը? *==', page.text)
    if hymatch:
        continue
    rupage, _ = convert_to(page, ruwiki)
    if not rupage or not rupage.exists():
        continue
    match = re.search(r'\{\{ *Население *\| *([^}]+?) *}}', rupage.text, flags=re.IGNORECASE)
    if not match:
        continue
    text_to_add = '== Բնակչություն ==\n{{ՌԴբնակչություն|' + match.group(1) + '}}'
    old_text = page.text
    page.text = re.sub(r'== *Ծանոթագրություններ *==', text_to_add + '\n\n== Ծանոթագրություններ ==', page.text)
    if old_text != page.text:
        page.save('+' + text_to_add, asynchronous=True)