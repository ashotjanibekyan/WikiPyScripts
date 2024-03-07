from typing import Any, List

import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import ExistingPageBot
import mwparserfromhell as mwp

from WikiCheckers.TranslateCiteDate import TranslateCiteDate
from WikiCheckers.ReformatCiteTemplates import ReformatCiteTemplates
from WikiCheckers.SimpleReplacements import SimpleReplacements
from WikiCheckers.ReformatSections import ReformatSections
from WikiCheckers.WikiChecker import WikiChecker


class CheckListBot(ExistingPageBot):
    actions = List[WikiChecker]
    parsed: mwp.wikicode

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.actions = []
        self.parsed = None
        self.actions.append(TranslateCiteDate(kwargs['site']))
        self.actions.append(ReformatCiteTemplates(kwargs['site']))
        self.actions.append(SimpleReplacements(kwargs['site']))
        self.actions.append(ReformatSections(kwargs['site']))
        print(self.actions)

    def init_page(self, item: Any):
        self.parsed = mwp.parse(item.text)
        return item

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        text = self.current_page.text
        summaries = []

        for action in self.actions:
            temp_text, update_summary = action.execute(text, self.parsed)
            if temp_text and temp_text != text and update_summary:
                text = temp_text
                summaries.append(update_summary)

        if text != self.current_page.text:
            self.put_current(text, summary=', '.join(summaries))


def main():
    """Parse command line arguments and invoke bot."""
    site = pywikibot.Site('hy', 'wikipedia')
    options = {}
    gen_factory = pagegenerators.GeneratorFactory()
    # Option parsing
    local_args = pywikibot.handle_args()  # global options
    local_args = gen_factory.handle_args(local_args)  # generators options
    for arg in local_args:
        opt, sep, value = arg.partition(':')
        if opt in ('-summary', '-text'):
            options[opt[1:]] = value
    CheckListBot(generator=gen_factory.getCombinedGenerator(), site=site, **options).run()


if __name__ == '__main__':
    main()
