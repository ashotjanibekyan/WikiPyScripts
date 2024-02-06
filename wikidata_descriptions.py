import pywikibot as pw
import pywikibot.config
from pywikibot import pagegenerators as pg
from random import randint
import requests
import re
from pywikibot.data import api

pywikibot.config.put_throttle = 3

site = pw.Site('wikidata', 'wikidata')

transJsonURL = "https://hy.wikipedia.org/w/index.php?title=Մասնակից:ԱշոտՏՆՂ/wikidataDescriptions.json&action=raw&ctype=text/json"
translations = requests.get(transJsonURL).json()
plainMap = translations["text"]
regexMap = translations["regex"]


def by_sparql(from_lang, from_desc, to_lang, to_desc, site):
    q = '''SELECT ?item WHERE {{
      ?item schema:description "{}"@{}.
      FILTER(NOT EXISTS {{
        ?item schema:description ?itemdesc.
        FILTER(LANG(?itemdesc) = "{}")
      }})
    }} limit 1000'''.format(from_desc, from_lang, to_lang)
    try:
        gen = pg.WikidataSPARQLPageGenerator(q, site)
        for item in gen:
            try:
                item.editDescriptions({to_lang: to_desc},
                                      summary='+{}:{} description based on {}:{}'.format(to_lang, to_desc, from_lang,
                                                                                         from_desc))
            except Exception as e:
                pass
        return True
    except:
        return False


def batch(qlist):
    req = api.Request(site=site, parameters={
        'action': 'wbgetentities',
        'ids': '|'.join(qlist),
        'props': 'descriptions',
        'languages': 'en|hy'
    })

    j = req.submit()
    if j['success']:
        for Q in qlist:
            if 'descriptions' not in j['entities'][Q]:
                continue
            desc = j['entities'][Q]['descriptions']
            if 'en' in desc and 'hy' not in desc:
                en_desc = desc['en']['value']
                if en_desc in plainMap and plainMap[en_desc]:
                    summary = f"+hy:{plainMap[en_desc]} description based on en:{en_desc}"
                    item = pw.ItemPage(site, Q)
                    item.editDescriptions({"hy": plainMap[en_desc]}, summary=summary)
                else:
                    for regex in regexMap:
                        if re.match(regex, en_desc):
                            item = pw.ItemPage(site, Q)
                            hy_desc = re.sub(regex, regexMap[regex], en_desc)
                            summary = f"+hy:{hy_desc} description based on en:{en_desc}"
                            item.editDescriptions({"hy": hy_desc}, summary=summary)


while True:
    try:
        translations = requests.get(transJsonURL).json()
        plainMap = translations["text"]
        regexMap = translations["regex"]
        Qs = list(set(['Q' + str(randint(1, 130000000)) for _ in range(5000)]))
        while Qs:
            batch(Qs[:50])
            Qs = Qs[50:]
    except Exception as ex:
        pass
