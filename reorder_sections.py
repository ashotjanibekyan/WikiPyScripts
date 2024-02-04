import re
from typing import List, Tuple, Any

import mwparserfromhell
import pywikibot
import pywikibot as pw
from pywikibot import pagegenerators as pg, Category
from pywikibot import textlib

site = pw.Site('hy', 'wikipedia')

defaultsort_pattern = r"\{\{\s*DEFAULTSORT:.*?\s*\}\}"

load_navs = False

source_templates = ['ԳՀ', 'ԴՄՀ', 'Հայ Սփյուռք հանրագիտարան', 'ՀԲ', 'ՀԲՀ', 'ՀԳԳՀ', 'ՀԵՀ', 'ՀՀ', 'ՀՀ2012',
                    'ՀՀՀ', 'ՀՍՀ', 'ՏՏՀ', 'ՏՏՀ', 'Պատմության թանգարանի նյութեր', 'ՂԱՊ', 'ՀԱԳ']


def is_sequence_complete(lst):
    return sorted(lst) == list(range(min(lst), max(lst) + 1))


def get_all_templates_and_redirects(gen):
    result = []
    for page in gen:
        if type(page) is str:
            page = pw.Page(site, page)
        result.append(page.title(with_ns=False))
        redirects = list(page.backlinks(filter_redirects=True))
        for redirect in redirects:
            result.append(redirect.title(with_ns=False))
    return result


def lower_list(l):
    return [i.lower() for i in l]


def load_templates(gen, file_name, use_file):
    result = []
    if use_file:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines_read = file.readlines()

        for line in lines_read:
            result.append(line.strip().lower())
    else:
        result = lower_list(get_all_templates_and_redirects(gen))
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(line + '\n' for line in result)
    return result


source_templates = load_templates(gen=[f'Կաղապար:{t}' for t in source_templates], file_name='source_templates.txt',
                                  use_file=True)
footer_templates = load_templates(gen=pw.Page(site, "Մասնակից:ԱշոտՏՆՂ/Ավազարկղ").linkedPages(),
                                  file_name='footer_templates.txt', use_file=True)
navBoxTemplates = load_templates(gen=pw.Category(site, 'Կատեգորիա:Վիքիպեդիա:Նավարկման կաղապարներ').members(),
                                 file_name='navboxes.txt', use_file=True)


def extract_pattern(text: str, regex: str) -> Tuple[str, str]:
    match = re.search(regex, text, flags=re.IGNORECASE)
    extracted = match.group(0) if match else None
    text_without_extracted = re.sub(regex, '', text, flags=re.IGNORECASE)
    return extracted, text_without_extracted


class Orderer:
    categories: list[Category]
    navbars: list[mwparserfromhell.wikicode.Template]
    subs: list[mwparserfromhell.wikicode.Template]
    source_ts: list[mwparserfromhell.wikicode.Template]
    footer_ts: list[mwparserfromhell.wikicode.Template]
    ac_template: mwparserfromhell.wikicode.Template
    tb_template: mwparserfromhell.wikicode.Template

    sections_map: list[list[int, mwparserfromhell.wikicode.Wikicode]]
    footer_parsed: mwparserfromhell.wikicode.Wikicode

    def __init__(self, page: pywikibot.Page):
        self.page = page
        self.initial_text = page.text
        self.initial_parsed = mwparserfromhell.parse(page.text)
        self.last_section_text = str(self.initial_parsed.get_sections()[-1])
        self.categories = []
        self.navbars = []
        self.subs = []
        self.source_ts = []
        self.footer_ts = []
        self.ac_template = None
        self.tb_template = None

        self.sections_map = []

    def process(self):
        if len(self.initial_parsed.get_sections()) <= 1:
            return self.initial_text
        if not self.process_sections():
            return self.initial_text
        self.process_footer()
        return self.reorder()

    def process_sections(self) -> bool:
        self.section_index_by_heading(['Տես նաև'])
        self.section_index_by_heading(['Նշումներ', 'Նշում'])
        self.section_index_by_heading(['Ծանոթագրություններ', 'Ծանոթագրություն', 'Ծանոթագրությունները'])
        self.section_index_by_heading(['Աղբյուրներ', 'Աղբյուր', 'Աղբյուրները'])
        self.section_index_by_heading('Գրականություն')
        self.section_index_by_heading(['Արտաքին հղումներ', 'Հղումներ'])

        return len(self.sections_map) > 1 and not self.unexpected_section_exists(self.sections_map) and not all(
            self.sections_map[i][0] <= self.sections_map[i + 1][0] for i in range(len(self.sections_map) - 1))

    def process_footer(self):
        inital_text = self.last_section_text
        self.categories = textlib.getCategoryLinks(self.last_section_text)
        self.last_section_text = textlib.removeCategoryLinks(self.last_section_text)
        self.defaultsort, self.last_section_text = extract_pattern(self.last_section_text, defaultsort_pattern)

        self.footer_parsed = mwparserfromhell.parse(self.last_section_text)
        templates: list[mwparserfromhell.wikicode.Template] = self.footer_parsed.filter_templates()
        for template in templates:
            name_c: str = template.name.lower().strip()
            if name_c.endswith('անավարտ') or name_c.lower().endswith('stub'):
                self.subs.append(template)
                self.footer_parsed.remove(template)
            elif name_c in navBoxTemplates:
                self.navbars.append(template)
                self.footer_parsed.remove(template)
            elif name_c in ('արտաքին հղումներ', 'ահ', 'authority control'):
                self.ac_template = template
                self.footer_parsed.remove(template)
            elif name_c in ('տաքսոնի նավարկում', 'տբ', 'taxonbar'):
                self.tb_template = template
                self.footer_parsed.remove(template)
            elif name_c in source_templates:
                self.source_ts.append(template)
                self.footer_parsed.remove(template)
            elif name_c in footer_templates:
                self.footer_ts.append(template)
                self.footer_parsed.remove(template)
            # self.dump_footer(inital_text)

    def dump_footer(self, inital_text):
        with open('dump.txt', 'a', encoding='utf-8') as file:
            file.writelines(f'\n======================================{page}=======================================\n' +
                            str(self.footer_parsed)[-500:] +

                            '\n-----------------------------------------------------------------------------------\n' +

                            inital_text[-500:] +

                            '\n====================================================================================\n')
        with open('templates.txt', 'a', encoding='utf-8') as temf:
            temf.writelines([str(t.name) + '\n' for t in self.footer_parsed.filter_templates()])

    def reorder(self):
        sections = self.initial_parsed.get_sections()
        sections = sections[:-len(self.sections_map)]
        last_section_title = self.footer_parsed.filter_headings()[0].title.strip()
        for section in self.sections_map:
            if section[1].filter_headings()[0].title.strip() == last_section_title:
                sections.append(str(self.footer_parsed))
            else:
                sections.append(section[1])
        content = '\n\n'.join([str(section).strip() for section in sections])

        footer_objects = mwparserfromhell.parse('')

        for el in self.source_ts:
            footer_objects.append(el)
        for el in self.footer_ts:
            footer_objects.append('\n' + str(el).strip())
        if self.tb_template is not None:
            footer_objects.append('\n' + str(self.tb_template).strip())
        if self.ac_template is not None:
            footer_objects.append('\n' + str(self.ac_template).strip())
        for el in self.navbars:
            footer_objects.append('\n' + str(el).strip())

        content += '\n\n' + str(footer_objects).strip()

        if self.defaultsort:
            content += '\n' + self.defaultsort

        content = textlib.replaceCategoryLinks(content, self.categories, site)
        content += '\n'.join([str(sub).strip() for sub in self.subs])
        return content

    def section_index_by_heading(self, heading_names):
        sections = self.initial_parsed.get_sections()
        for i in range(len(sections)):
            headings = sections[i].filter_headings()
            if headings and headings[0].title.strip() in heading_names:
                self.sections_map.append([i, sections[i]])
                return i
        return -1

    def unexpected_section_exists(self, sections_map):
        sections = self.initial_parsed.get_sections()
        max_index = max(sections_map, key=lambda x: x[0])
        last_index = len(sections) - 1
        return max_index == last_index and is_sequence_complete(list(map(lambda x: x[0], sections_map)))


gen = pg.RandomPageGenerator(namespaces=[0], site=site)
for page in gen:
    orderer = Orderer(page)
    new_text = orderer.process()
    if new_text != page.text:
        page.text = new_text
        page.save('փոխում եմ բաժինների հերթականությունը ըստ կանոնակարգի')