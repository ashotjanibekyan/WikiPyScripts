import mwparserfromhell
import pywikibot


class WikiChecker:
    site: pywikibot.Site

    def __init__(self, site: pywikibot.Site):
        self.site = site

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        pass
