import json

import pywikibot as pw
from pywikibot import pagegenerators as pg
import mwparserfromhell as mwp

site = pw.Site('hy', 'wikipedia')


def get_bad_urls():
    list_page = pw.Page(site, 'Մասնակից:ԱշոտՏՆՂ/կասկածելի_կայքեր.json')
    return list(json.loads(list_page.text))


def process_url(url):
    text = f'== {url} =='
    surl = url.replace('\\', '\\\\')
    surl = surl.replace('.', '\\.')
    surl = surl.replace('/', '\\/')
    gen = list(pg.SearchPageGenerator(query='insource:/' + surl + '/', namespaces=[0], site=site))
    for page in gen:
        parsed = mwp.parse(page.text)
        for tag in parsed.filter_tags():
            if tag.tag == 'ref':
                if url in str(tag):
                    text += f'\n# [[{page.title()}]]'
                    break
    return text


def main():
    urls = get_bad_urls()
    text = ''
    for url in urls:
        text += '\n' + process_url(url)
    header = 'Այս էջում գտնվում են այն հոդվածները, որոնք ծանոթագրության մեջ օգտագորոծում են կասկածելի կայք։ '\
             'Դիտարկվող կայքերի ցանկը գտնվում է [[Մասնակից:ԱշոտՏՆՂ/կասկածելի_կայքեր.json]] էջում։ '\
             'Այս կայքերը ցանկացած ձևով (օրինակ՝ նաև արտաքին հղումներում) օգտագործող էջերի համար՝ [[Սպասարկող:LinkSearch]]։'

    page = pw.Page(site, 'Վիքիպեդիա:Ցանկեր/կասկածելի աղբյուրներով հոդվածներ')
    page.text = header + '\n' + text
    page.save('թարմացում')


main()
