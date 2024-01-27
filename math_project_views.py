import pywikibot as pw
import pywikibot.data.api as api

from helpers import matrix_to_wikitable

hywiki = pw.Site('hy', 'wikipedia')
enwiki = pw.Site('en', 'wikipedia')


def get_views(page):
    s = 0
    try:
        req = api.Request(site=hywiki, parameters={'action': 'query',
                                                   'titles': page,
                                                   'prop': 'pageviews'})
        page_views = req.submit()['query']['pages'][str(page.pageid)]['pageviews']
        for day in page_views:
            if page_views[day]:
                s += page_views[day]
    except Exception as e:
        pass
    return s


cat = pw.Category(hywiki, 'Կատեգորիա:Մաթեմատիկական հոդվածներ')
data = []
for talkpage in cat.members():
    main_page = talkpage.toggleTalkPage()
    views = get_views(main_page)
    data.append([main_page, views])

data = [['Հոդված', 'Դիտումներ (վերջին 60 օրվա ընթացքում)']] + sorted(data[1:], key=lambda x: x[1], reverse=True)
viewpage = pw.Page(hywiki, 'Վիքինախագիծ:Մաթեմատիկա/Հաճախ դիտվող')
viewpage.text = matrix_to_wikitable(None, data[:501]).replace('[[hy:', '[[')
viewpage.save(summary='թարմացում')