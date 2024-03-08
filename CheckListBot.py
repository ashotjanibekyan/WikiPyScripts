from typing import Any, List

import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import ExistingPageBot
import mwparserfromhell as mwp

from WikiCheckers.TranslateCiteDate import TranslateCiteDate
from WikiCheckers.ReformatTemplates import ReformatTemplates
from WikiCheckers.SimpleReplacements import SimpleReplacements
from WikiCheckers.FixCiteTemplates import FixCiteTemplates
from WikiCheckers.ReformatSections import ReformatSections
from WikiCheckers.WikiChecker import WikiChecker


class CheckListBot(ExistingPageBot):
    actions = List[WikiChecker]
    parsed: mwp.wikicode

    def __init__(self, **kwargs: Any):
        self.update_options.update(kwargs)
        super().__init__(**kwargs)
        self.actions = []
        self.parsed = None

        cs1_cite_templates = [
            'Citation', 'Cite arXiv', 'Cite AV media', 'Cite AV media notes', 'Cite bioRxiv', 'Cite book', 'Cite web',
            'Cite CiteSeerX', 'Cite conference', 'cite document', 'Cite encyclopedia', 'Cite episode', 'Cite interview',
            'Cite journal', 'Cite magazine', 'Cite map', 'Cite medRxiv', 'Cite news', 'Cite thesis', 'Cite podcast',
            'Cite press release', 'Cite report', 'Cite mailing list', 'Cite SSRN', 'Cite tech report'
        ]

        inline_templates = ['Ռուսերեն գիրք', 'Ռուսերեն հոդված']

        infobox = ['Տեղեկաքարտ Բնակավայր', 'Տեղեկաքարտ Անձ', 'Տեղեկաքարտ Գրող', 'Տեղեկաքարտ Ֆիլմ']
        reformatData = {}
        reformatData.update({t: 'inline' for t in cs1_cite_templates})
        reformatData.update({t: 'inline' for t in inline_templates})
        reformatData.update({t: 'block' for t in infobox})

        self.actions.append(FixCiteTemplates(kwargs['site'],cs1_cite_templates))
        self.actions.append(TranslateCiteDate(kwargs['site'], cs1_cite_templates))
        self.actions.append(ReformatTemplates(kwargs['site'], reformatData))
        self.actions.append(SimpleReplacements(kwargs['site']))
        self.actions.append(ReformatSections(kwargs['site']))

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
    local_args = pywikibot.argvu[1:]
    if len(local_args) == 0:
        local_args = ['-recentchanges:0,1800', '-ns:0', '-always']
    local_args = pywikibot.handle_args(local_args)  # global options
    local_args = gen_factory.handle_args(local_args)  # generators options
    for arg in local_args:
        opt, sep, value = arg.partition(':')
        if opt in ('-summary', '-text'):
            options[opt[1:]] = value
        elif opt in ('-always', ):
            options[opt[1:]] = True
    CheckListBot(generator=gen_factory.getCombinedGenerator(), site=site, **options).run()


if __name__ == '__main__':
    main()
