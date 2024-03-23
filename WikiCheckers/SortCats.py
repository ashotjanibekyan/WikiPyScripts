import mwparserfromhell
import pywikibot
from pywikibot import textlib

from WikiCheckers.WikiChecker import WikiChecker


class SortCats(WikiChecker):
    def __init__(self, site: pywikibot.Site):
        super().__init__(site)

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        categories = textlib.getCategoryLinks(site=self.site, text=text)
        categories.sort()
        return textlib.replaceCategoryLinks(text, categories), 'դաս․ կատ․'
