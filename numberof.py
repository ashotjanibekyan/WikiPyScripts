#!/usr/bin/python
# -*- coding: utf-8 -*-
# original version at https://es.wikipedia.org/wiki/Usuario:Bigsus-bot/Variables.py
import pywikibot, re
from urllib.request import urlopen

parameters = {

    'wikiquote': {
        'hy': {
            'prepend': u'<!-- Ցանկը պարբերաբար թարմացվում է բոտի կողմից, խնդրում ենք կաղապարում փոփոխություններ չանել, քանի որ դրանք չեղարկվելու են հաջորդ թարմացմամբ։ Փոխարենը կարող եք ձեր առաջրկությունները անել քննարկման էջում -->',
            'summary': u'Թարմացնում եմ տվյալները',
            'page': u'Template:NUMBEROF/data',
            'end': u'<noinclude>[[Կատեգորիա:Վիքիքաղվածք:Տեղեկաքարտերի ենթաէջեր]]</noinclude>'
        }
    },
    'wikipedia': {
        'hy': {
            'prepend': u'<!-- Ցանկը պարբերաբար թարմացվում է բոտի կողմից, խնդրում ենք կաղապարում փոփոխություններ չանել, քանի որ դրանք չեղարկվելու են հաջորդ թարմացմամբ։ Փոխարենը կարող եք ձեր առաջրկությունները անել քննարկման էջում -->',
            'summary': u'Թարմացնում եմ տվյալները',
            'page': u'Template:NUMBEROF/data',
            'end': u'<noinclude>[[Կատեգորիա:Վիքիպեդիա:Տեղեկաքարտերի ենթաէջեր]]</noinclude>'
        }
    },
    'wiktionary': {
        'hy': {
            'prepend': u'<!-- Ցանկը պարբերաբար թարմացվում է բոտի կողմից, խնդրում ենք կաղապարում փոփոխություններ չանել, քանի որ դրանք չեղարկվելու են հաջորդ թարմացմամբ։ Փոխարենը կարող եք ձեր առաջրկությունները անել քննարկման էջում -->',
            'summary': u'Թարմացնում եմ տվյալները',
            'page': u'Template:NUMBEROF/data',
            'end': u'<noinclude>[[Կատեգորիա:Վիքիբառարան:Տեղեկաքարտերի ենթաէջեր]]</noinclude>'
        }
    }
}

data = []


def getdata(wiki):
    langs = pywikibot.Site('hy', wiki).languages()

    reg = r"\"pages\":(?P<total>.*),\"articles\":(?P<good>\d*),\"edits\":(?P<edits>\d*),\"images\":(?P<images>\-?\d*),\"users\":(?P<users>\d*),\"activeusers\":(?P<activeusers>\d*),\"admins\":(?P<admins>\d*),\"jobs\":(?P<jobs>\d*)"

    totalT = 0
    articleT = 0
    editsT = 0
    imagesT = 0
    usersT = 0
    activeusersT = 0
    adminsT = 0

    for i in langs:
        try:
            rec = urlopen(
                'https://%s.%s.org/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json' % (i, wiki))
            downloadstats = rec.read().decode('utf-8')
            stats = re.search(reg, downloadstats)
            if stats is None:
                continue

            data.insert(0, [i,
                            int(stats.group('total')),
                            int(stats.group('good')),
                            int(stats.group('edits')),
                            int(stats.group('images')),
                            int(stats.group('users')),
                            int(stats.group('activeusers')),
                            int(stats.group('admins'))
                            ])
            totalT += data[0][1]
            articleT += data[0][2]
            editsT += data[0][3]
            imagesT += data[0][4]
            usersT += data[0][5]
            activeusersT += data[0][6]
            adminsT += data[0][7]
        except Exception:
            pass

    data.append(['total', totalT, articleT, editsT, imagesT, usersT, activeusersT, adminsT])

    new = u'<onlyinclude>{{#switch:{{{1}}}\n| date = Վերջին անգամ թարմացվել է {{subst:lc:{{subst:#time: Y թվականի Fի j|+4 hours}}}}-ին՝ Երևանի ժամանակով {{subst:#time:H:i|+4 hours}}-ին։\n'
    new += u"| {{subst:CONTENTLANG}}2 = {{#switch:{{{2}}}"
    new += u"\n\t| NUMBEROFARTICLES | ARTICLES = {{NUMBEROFARTICLES:R}}"
    new += u"\n\t| NUMBEROFFILES | FILES = {{NUMBEROFFILES:R}}"
    new += u"\n\t| NUMBEROFPAGES |PAGES = {{NUMBEROFPAGES:R}}"
    new += u"\n\t| NUMBEROFUSERS | USERS = {{NUMBEROFUSERS:R}}"
    new += u"\n\t| NUMBEROFACTIVEUSERS | ACTIVEUSERS = {{NUMBEROFACTIVEUSERS:R}}"
    new += u"\n\t| NUMBEROFADMINS | ADMINS = {{NUMBEROFADMINS:R}}"
    new += u"\n\t| NUMBEROFEDITS | EDITS = {{NUMBEROFEDITS:R}}"
    new += u"\n\t| 0 }}\n"
    for values in data:
        new += u"| " + values[0] + u' = {{#switch:{{{2}}}'
        new += u"\n\t| NUMBEROFPAGES | PAGES = " + str(values[1])
        new += u"\n\t| NUMBEROFARTICLES | ARTICLES = " + str(values[2])
        new += u"\n\t| NUMBEROFEDITS | EDITS = " + str(values[3])
        new += u"\n\t| NUMBEROFFILES | FILES = " + str(values[4])
        new += u"\n\t| NUMBEROFUSERS | USERS = " + str(values[5])
        new += u"\n\t| NUMBEROFACTIVEUSERS | ACTIVEUSERS = " + str(values[6])
        new += u"\n\t| NUMBEROFADMINS | ADMINS = " + str(values[7])
        new += u"\n\t| 0 }}\n"
    new += u"| 0 }}</onlyinclude>"

    return new


for wiki in parameters:
    new = getdata(wiki)
    for lang in parameters[wiki]:
        new = parameters[wiki][lang]['prepend'] + new + parameters[wiki][lang]['end']
        page = pywikibot.Page(pywikibot.Site(lang, wiki), parameters[wiki][lang]['page'])
        page.put(new, parameters[wiki][lang]['summary'])
        data = []
