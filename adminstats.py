import pywikibot as pw
from datetime import date
from dateutil.relativedelta import relativedelta

hywiki = pw.Site('hy', 'wikipedia')
admins = []
gen = hywiki.allusers(group='sysop')

for user in gen:
    if user['name'] != 'Abuse filter':
        admins.append(pw.User(hywiki, user['name']))

print(admins)

six_months = date.today() + relativedelta(months=-6)
total = {}
nss = ['Հիմնական', 'Պատկեր', 'Կաղապար', 'Կատեգորիա', 'patrol']
logtyps = ['delete', 'block', 'abusefilter', 'rights', 'merge', 'protect', 'MediaWiki', 'contentmodel']

for admin in admins:
    total[admin.username] = {}
    cs = admin.contributions(end=str(six_months) + 'T00:00:00.000Z', total=0)
    ls = admin.logevents(end=str(six_months) + 'T00:00:00.000Z', total=0)

    for c in cs:
        ns = c[0].namespace().custom_name
        if ns == '':
            ns = 'Հիմնական'
        if ns in total[admin.username]:
            total[admin.username][ns] += 1
        else:
            total[admin.username][ns] = 1

    for l in ls:
        if l.type() in total[admin.username]:
            total[admin.username][l.type()] += 1
        else:
            total[admin.username][l.type()] = 1


def activities_table(title, activities, actTypes, num):
    t = '{| class="wikitable sortable"\n'
    t += '|-\n'
    t += '!' + title + '!!' + '!!'.join(i.username for i in admins) + '\n'

    for actType in actTypes:
        line = [actType]
        for i in range(len(admins)):
            if actType in activities[admins[i].username]:
                line.append(str(activities[admins[i].username][actType]))
            else:
                line.append(str(0))

        t += '|-\n'
        t += '|' + '||'.join(line) + '\n'

    total = ['Ընդամենը']
    for admin in admins:
        activities[admin.username]['Ընդամենը'] = 0
        for actType in actTypes:
            if actType in activities[admin.username]:
                activities[admin.username]['Ընդամենը'] += activities[admin.username][actType]
        total.append(activities[admin.username]['Ընդամենը'])

    t += '|-\n'
    t += '|Ընդամենը||' + '||'.join(
        ['style="background: #33f85f;"|' + str(_) if _ >= num else 'style="background: #ff0000;"|' + str(_) for _ in
         total[1:]]) + '\n'

    t += '|}'
    return t


editsTable = activities_table('Խմբագրումներ', total, nss, 50)
logsTable = activities_table('Գործողություն', total, logtyps, 25)

page = pw.Page(hywiki, 'Վիքիպեդիա:Ադմինիստրատոր/Վիճակագրություն')
page.text = editsTable + '\n\n' + logsTable
page.save(summary='թարմացում', botflag=False)
