import re, pywikibot

def col2ver(match):
    if match.group(1)[-1].isnumeric() and match.group(2) and match.group(2)[0].isnumeric():
        return match.group(0)

    if match.group(2) and not re.match(r'[\s}»<|]', match.group(2)[0]):
        return match.group(0)

    if match.group(2):
        return match.group(1) + '։' + match.group(2)
    else:
        return match.group(1) + '։'

fixes['col2ver'] = {
    'regex': True,
    'msg': {
        'hy': 'Colon֊ը (:, U+003A) փոխարինում եմ հայերեն վերջակետով (։, U+0589)',
    },
    'replacements': [
        (r'([:,`։՝])((?:(?:<ref[^>]*\/>)|(?:<ref[^>\/]*>(?:[\s\S](?!\/ref>)|(?:{{sfn[^}]+}}))+<\/ref>))+)', r'\2\1', 'ծանոթագրությունը տեղափոխում եմ կետադրական նշանից առաջ'),
        (r"([ա-ևԱ-Ֆ][ \d(')»`%\]:,\-²]*(?:(?:<ref[^>]*\/>)|(?:<ref[^>\/]*>(?:[\s\S](?!\/ref>))+<\/ref>)|(?:{{sfn[^}]+}}))*):([\s\S]{0,5})", col2ver),
        (r'([ա-ևԱ-Ֆ]<(sup|sub)>\d+<\/\2>):(\s)', r'\1։\3')
    ],
    'exceptions': {
        'inside-tags': ['file', 'gallery', 'category', 'timeline', 'hyperlink']
    },
    'generator': [
        '-start:! -ns:0'
    ]
}

def redirlinks(m):
    hywiki = pywikibot.Site('hy', 'wikipedia')
    try:
        left_page = pywikibot.Page(hywiki, m.group(1))
        if not left_page.exists():
            return m.group(0)
        if left_page.isRedirectPage():
            left_page = left_page.getRedirectTarget()
        i = 0
        while len(m.group(2)) > i and i < 4:
            if m.group(2)[len(m.group(2))-i:] and not re.match(r'[a-zA-Zա-ևԱ-Ֆ]+', m.group(2)[len(m.group(2))-i:]):
                break
            right_page = pywikibot.Page(hywiki, m.group(2)[:len(m.group(2))-i])
            temp = None
            if right_page.exists() and right_page.isRedirectPage():
                temp = right_page.getRedirectTarget()
            if left_page == right_page or left_page == temp:
                return '[[' + right_page.title() + ']]' + m.group(2)[len(m.group(2))-i:]
            i+=1
    except pywikibot.exceptions.InvalidTitle as e:
        pass
    return m.group(0)

fixes['redirlinks'] = {
    'regex': True,
    'msg': {
        'hy': 'պարզեցնում եմ ներքին հղումները'
    },
    'replacements': {
        (r'\[\[([^|\]]+)\|([^\]]+)\]\]', redirlinks)
    }
}
