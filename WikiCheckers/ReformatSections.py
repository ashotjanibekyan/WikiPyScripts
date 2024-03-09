import re

import mwparserfromhell
import pywikibot

from WikiCheckers.WikiChecker import WikiChecker


class ReformatSections(WikiChecker):

    def __init__(self, site: pywikibot.Site):
        super().__init__(site)

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        text = str(parsed)
        for header in parsed.filter_headings():
            ht = header.title.strip()
            ht = re.sub(r"^('+) *(.+?) *\1", r'\2', ht)
            header.title = f' {ht} '
        for section in parsed.get_sections():
            parsed.replace(section, f'{str(section).strip()}\n\n')
        new_text = str(parsed)
        new_text = re.sub(r'(\n(=+)[^=]+\2)\s+', r'\1\n', new_text)
        new_text = new_text.strip()
        if new_text != text:
            return new_text, None
        return None, None
