import toolforge
import pywikibot as pw

import helpers

hywiki, ruwiki = helpers.get_wikipedias('hy', 'ru')


def ruwiki_people_with_fi():
    conn = toolforge.connect('ruwiki')
    sql = '''SELECT page_title
        FROM page
        JOIN imagelinks ON il_from = page_id
        WHERE il_to IN
                (SELECT page_title
                 FROM page
                 JOIN categorylinks ON cl_from = page_id
                 WHERE cl_to = 'Файлы:Несвободные_фотографии_умерших')'''
    rutitles = {}
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        for r in results:
            rutitles[r[0].decode('utf-8').replace('_', ' ')] = True

    return rutitles


RU_TITLES = None


def is_addable(title, check_ru):
    global RU_TITLES
    global ruwiki
    if check_ru and RU_TITLES == None:
        RU_TITLES = ruwiki_people_with_fi()
    try:
        page = pw.Page(hywiki, title)
        item = pw.ItemPage.fromPage(page, lazy_load=True)
        if item.claims and 'P18' in item.claims:
            return False
        if check_ru:
            to_link = item.sitelinks.get('ruwiki')
            return to_link and to_link.title in RU_TITLES
        return True
    except Exception as e:
        return False


def process_year(year, check_ru=False):
    conn = toolforge.connect('hywiki')
    sql = '''SELECT p1.page_title
        FROM page p1
        JOIN categorylinks ON p1.page_id = cl_from
        WHERE cl_to = '{}_մահեր'
          AND p1.page_namespace = 0
          AND p1.page_title NOT IN
            (SELECT p2.page_title
             FROM page p2
             JOIN imagelinks ON p2.page_id = il_from
             WHERE EXISTS
                 (SELECT 1
                  FROM image
                  WHERE img_name = il_to))'''.format(year)
    pages_without_images = []
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        for r in results:
            title = r[0].decode('utf-8').replace('_', ' ')
            if is_addable(title, check_ru):
                pages_without_images.append(title)
    return pages_without_images


def run(check_ru):
    global RU_TITLES
    table = {}

    for year in range(1950, 2025):
        year_data = process_year(year, check_ru)
        if year_data:
            table[year] = year_data

    text = ''
    for year in table:
        text += f'\n== {year} մահեր ==\n'
        for article in table[year]:
            text += f'# [[{article}]]\n'
    title = 'Վիքիպեդիա:Համագործակցություն/մահացած անձանց հոդվածներ, որոնք պատկեր չունեն'
    if check_ru:
        title += '/ruwiki-ում կա'

    page_pw = pw.Page(hywiki, title)
    page_pw.text = text
    page_pw.save('թարմացում', botflag=False)
    RU_TITLES = None

is_addable("Ալբերտ Այնշտայն", False)
run(True)
run(False)
