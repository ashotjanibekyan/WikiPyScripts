import re

import mwparserfromhell
import pywikibot

from WikiCheckers.WikiChecker import WikiChecker


class SimpleReplacements(WikiChecker):
    def __init__(self, site: pywikibot.Site):
        super().__init__(site)

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        text = str(parsed)
        summaries = []
        without_nowiki = re.sub(r'<nowiki */>', '', text)
        if without_nowiki != text:
            summaries.append('-<nowiki/>')
            text = without_nowiki
        return text, ', '.join(summaries)