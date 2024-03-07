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
        no_space_before_ref = re.sub(r' +<ref', '<ref', without_nowiki)
        if no_space_before_ref != text:
            summaries.append('- <ref, +<ref')
            text = no_space_before_ref
        return text, ', '.join(summaries)