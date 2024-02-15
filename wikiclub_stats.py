import openpyxl
import pandas as pd
from io import BytesIO
import pywikibot as pw
import json
import requests
from pywikibot.data.api import ListGenerator

import helpers

spreadsheetId = "189UVd_hAjuobDns2jqX-36DQP23GkSE_77O6KDzds-E"  # Please set your Spreadsheet ID.
url = "https://docs.google.com/spreadsheets/export?exportFormat=xlsx&id=" + spreadsheetId
res = requests.get(url)
data = BytesIO(res.content)
xlsx = openpyxl.load_workbook(filename=data)

Clubs = {
    'Լեռնապատ': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Լեռնապատի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Լեռնապատ',
        'pop': 2279,
        'name': 'Լեռնապատ',
        'users': []
    },
    'Գորիս': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Գորիսի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Գորիսի վիքիակումբ',
        'pop': 20300,
        'name': 'Գորիս',
        'users': []
    },
    'Դդմաշեն': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Դդմաշենի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Դդմաշենի վիքիակումբ',
        'pop': 2876,
        'name': 'Դդմաշեն',
        'users': []
    },
    'Կիրանց': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Կիրանցի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Կիրանց',
        'pop': 352,
        'name': 'Կիրանց',
        'users': []
    },
    'Կողբ': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Կողբի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Կողբի վիքիակումբ',
        'pop': 5300,
        'name': 'Կողբ',
        'users': []
    },
    'Հացիկ': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Հացիկի վիքիակումբ/Վիճակագրություն',
        'wikisource': 'Վիքիդարան:Կրթական ծրագիր/Հացիկի վիքիակումբ',
        'pop': 1044,
        'name': 'Հացիկ',
        'users': []
    },
    'Ջերմուկ': {
        'wikipedia': 'Վիքիպեդիա:Կրթական ծրագիր/Ջերմուկի վիքիակումբ/Վիճակագրություն',
        'pop': 4300,
        'name': 'Ջերմուկ',
        'users': []
    }
}

for key in Clubs:
    values = pd.read_excel(data, sheet_name=key)
    Clubs[key]['users'] += values['Մասնակցային անուն'].dropna().str.strip().tolist()

wikipedia = pw.Site('hy', 'wikipedia')
wikisource = pw.Site('hy', 'wikisource')
wiktionary = pw.Site('hy', 'wiktionary')
wikidata = pw.Site('wikidata', 'wikidata')


def get_wikidata_edit_count(user, start, end):
    return len(list(pw.User(wikidata, user).contributions(total=-1,
                                                          start=start + "T00:00:00.000Z",
                                                          end=end + "T00:00:00.000Z")))


def is_category_added(edit, catname):
    api = '/w/api.php?action=query&format=json&prop=categories&utf8=1&revids='
    aR = requests.get('https://hy.wikisource.org/' + api + str(edit['revid']))
    aData = json.loads(aR.content)
    isAfter = False
    if 'categories' in aData['query']['pages'][str(edit['pageid'])]:
        aCategories = aData['query']['pages'][str(edit['pageid'])]['categories']
        for aCat in aCategories:
            if aCat['title'] == catname:
                isAfter = True
    if 'new' in edit:
        return isAfter
    bR = requests.get('https://hy.wikisource.org/' + api + str(edit['parentid']))
    bData = json.loads(bR.content)
    isBefore = False
    if 'categories' in bData['query']['pages'][str(edit['pageid'])]:
        bCategories = bData['query']['pages'][str(edit['pageid'])]['categories']
        for bCat in bCategories:
            if bCat['title'] == catname:
                isAfter = True
    if isAfter and not isBefore:
        return True
    else:
        return False


def user_stat(project, username, start, end):
    addedBytes = 0
    removedBytes = 0
    edits = 0
    newPages = 0
    proofread = 0
    validate = 0

    site = wikipedia if project == 'wikipedia' else wikisource
    user = pw.User(site, username)
    ucgen = site._generator(ListGenerator, type_arg='usercontribs',
                            ucprop='timestamp|ids|sizediff|title|flags',
                            total=-1)
    ucgen.request['ucuser'] = user
    ucgen.request['ucstart'] = start + "T00:00:00.000Z"
    ucgen.request['ucend'] = end + "T00:00:00.000Z"

    for edit in ucgen:
        if edit['ns'] == 0 or (project == 'wikisource' and edit['ns'] == 104):
            edits += 1
            if 'new' in edit:
                newPages += 1
            if project == 'wikisource' and is_category_added(edit, 'Կատեգորիա:Սրբագրված'):
                proofread += 1
            if project == 'wikisource' and is_category_added(edit, 'Կատեգորիա:Հաստատված'):
                validate += 1

            if edit['sizediff'] < 0:
                removedBytes += edit['sizediff']
            else:
                addedBytes += edit['sizediff']
    if project == 'wikisource':
        return [addedBytes, removedBytes, edits, newPages, proofread, validate]
    else:
        return [addedBytes, removedBytes, edits, newPages, get_wikidata_edit_count(username, start, end)]


def get_club_data(club, start, end):
    club_stats = {'wikipedia': []}
    if 'wikisource' in club:
        club_stats['wikisource'] = []

    for user in club['users']:
        user = user.strip()
        user_s = user_stat('wikipedia', user, start, end)
        if sum(user_s) > 0:
            club_stats['wikipedia'].append([user] + user_s)
        if 'wikisource' in club_stats:
            user_s = user_stat('wikisource', user, start, end)
            if sum(user_s) > 0:
                club_stats['wikisource'].append([user] + user_s)

    club_stats['wikipedia_total'] = [club['name']] + [sum(cell for cell in column[1:] if isinstance(cell, (int, float)))
                                                      for column in zip(*club_stats['wikipedia'])]

    if 'wikisource' in club_stats:
        club_stats['wikisource_total'] = [club['name']] + [
            sum(cell for cell in column[1:] if isinstance(cell, (int, float))) for column in
            zip(*club_stats['wikisource'])]
    return club_stats


def get_stats(start, end):
    for club in Clubs:
        Clubs[club]['stats'] = get_club_data(Clubs[club], start, end)


def run(start, end, subtitle):
    get_stats(start, end)
    club_total_wikipedia = [
        ['Մասնակցային անուն', 'Բայթեր (+)', 'Բայթեր (-)', 'Խմբագրումներ', 'Հոդվածներ', 'Վիքիտվյալներ']]
    club_total_wikisource = [
        ['Մասնակցային անուն', 'Բայթեր (+)', 'Բայթեր (-)', 'Խմբագրումներ', 'Ստեղծված', 'Սրբագրված', 'Հաստատված']]

    for key in Clubs:
        club_stats = Clubs[key]['stats']
        wikipedia_matrix = [['Մասնակցային անուն', 'Բայթեր (+)', 'Բայթեր (-)', 'Խմբագրումներ',
                              'Ստեղծված', 'Սրբագրված', 'Հաստատված']] + club_stats['wikisource']
        wikipedia_matrix.append(club_stats['wikipedia_total'])
        wikipedia_table = helpers.matrix_to_wikitable(wikipedia_matrix)
        wikipedia_page = pw.Page(wikipedia, f"{Clubs[key]['wikipedia']}/{subtitle}")
        wikipedia_page.text = wikipedia_table
        # wikipedia_page.save('թարմացում')
        club_total_wikipedia += club_stats['wikipedia']
        if 'wikisource' in club_stats and club_stats['wikisource']:
            wikisource_matrix = [['Մասնակցային անուն', 'Բայթեր (+)', 'Բայթեր (-)', 'Խմբագրումներ',
                                  'Ստեղծված', 'Սրբագրված', 'Հաստատված']] + club_stats['wikisource']
            wikisource_matrix.append(club_stats['wikisource_total'])
            wikisource_table = helpers.matrix_to_wikitable(wikisource_matrix)
            wikisource_page = pw.Page(wikisource, f"{Clubs[key]['wikisource']}/{subtitle}")
            wikisource_page.text = wikisource_table
            # wikisource_page.save('թարմացում')
            club_total_wikisource += club_stats['wikisource']

    club_total_wikipedia.append(['Ընդհանուր'] + [sum(cell for cell in column[1:] if isinstance(cell, (int, float)))
                                                 for column in zip(*club_total_wikipedia)])
    club_total_wikipedia_table = helpers.matrix_to_wikitable(club_total_wikipedia)
    club_total_wikipedia_page = pw.Page(wikipedia,
                                        f"Վիքիպեդիա:Նախագիծ:Կրթական ծրագիր/Համագործակցություն ավագ դպրոցների հետ/Հաշվետվություն/{subtitle}")
    club_total_wikipedia_page.text = club_total_wikipedia_table
    # club_total_wikipedia_page.save('թարմացում')

    club_total_wikisource.append(['Ընդհանուր'] + [sum(cell for cell in column[1:] if isinstance(cell, (int, float)))
                                                  for column in zip(*club_total_wikisource)])
    club_total_wikisource_table = helpers.matrix_to_wikitable(club_total_wikisource)
    club_total_wikisource_page = pw.Page(wikisource,
                                         f"Վիքիդարան:Համագործակցություն Վիքիակումբների հետ/Վիճակագրություն/Ընդհանուր/{subtitle}")
    club_total_wikisource_page.text = club_total_wikisource_table
    club_total_wikisource_page.save('թարմացում')


run('2024-02-01', '2024-01-01', 'Հունվար, 2024')