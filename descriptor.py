#!/usr/bin/python
# -*- coding: utf-8 -*-

# Pywikibot will automatically set the user-agent to include your username.
# To customise the user-agent see
# https://www.mediawiki.org/wiki/Manual:Pywikibot/User-agent
import sys

import pywikibot
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator
from pywikibot.bot import SingleSiteBot
from pywikibot.data import api

pywikibot.config.put_throttle = 1


class WikidataQueryBot(SingleSiteBot):
    def __init__(self, generator, en_desc, hy_desc, **kwargs):
        super(WikidataQueryBot, self).__init__(**kwargs)
        self.generator = list(generator)
        print(len(self.generator))
        self.en_desc = en_desc
        self.hy_desc = hy_desc

    def treat(self, page):
        r = pywikibot.data.api.Request(site, parameters={
            "action": "wbsetdescription",
            "format": "json",
            "id": page.title(),
            "summary": f"based on en:{self.en_desc}",
            "language": "hy",
            "value": self.hy_desc,
            "token": site.tokens['csrf'],
            "formatversion": "2"
        })
        r.submit()


if __name__ == '__main__':
    search_term = sys.argv[1]

    query = f"""SELECT ?item WHERE {{
      ?item schema:description "{search_term}"@en.
      FILTER(NOT EXISTS {{
        ?item schema:description ?itemdesc.
        FILTER(LANG(?itemdesc) = "hy")
      }})
    }}"""
    site = pywikibot.Site('wikidata', 'wikidata')
    gen = WikidataSPARQLPageGenerator(query, site=site.data_repository(),
                                      endpoint='https://query.wikidata.org/sparql')
    bot = WikidataQueryBot(gen, en_desc=search_term, hy_desc=sys.argv[2], site=site)
    bot.run()
