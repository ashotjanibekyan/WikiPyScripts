from PIL import Image
import toolforge
import pywikibot as pw
from io import BytesIO
import os
import requests, re
from pywikibot.data import api

URL = "https://hy.wikipedia.org/w/api.php"
hywiki = pw.Site('hy', 'wikipedia')


def get_revs_to_del(image_name):
    get_old_rev = {'action': 'query',
                   'prop': 'imageinfo',
                   'titles': image_name,
                   'iiprop': 'archivename',
                   'iilimit': 'max',
                   'formatversion': 2}

    request = api.Request(site=hywiki, **get_old_rev)
    r = request.submit()
    data = r['query']['pages'][0]['imageinfo'][1:]
    result = []
    for i in data:
        if 'archivename' in i:
            result.append(i['archivename'])
    return result


def delete_old_revs(image_name):
    old_revs = get_revs_to_del(image_name)
    for old_rev in old_revs:
        version = re.sub(r'([^!]*)!.*', r'\1', old_rev)
        title = re.sub(r'[^!]*!(.*)', r'\1', old_rev)
        delete_old_rev = {
            'action': "revisiondelete",
            'target': title,
            'type': 'oldimage',
            'hide': 'content',
            'ids': version,
            'reason': 'Չօգտագործվող նիշք',
            'token': hywiki.tokens['csrf']
        }
        request = pw.data.api.Request(site=hywiki, **delete_old_rev, use_get=False)
        request.submit()


conn = toolforge.connect('hywiki')


def resize_and_upload(query):
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            file = pw.FilePage(hywiki, r[0].decode('utf-8'))
            url = file.get_file_url()
            response = requests.get(url)
            try:
                img = Image.open(BytesIO(response.content))
            except OSError as e:
                continue
            if max(img.height, img.width) <= 600:
                continue
            ratio = 600 / max(img.height, img.width)
            h = int(img.height * ratio)
            w = int(img.width * ratio)
            img = img.resize((w, h), Image.LANCZOS)
            img.save(file.title())
            file.upload(file.title(), comment='կանոնակարգին համապատասխանող փոքր տարբերակ', ignore_warnings=True)
            os.remove(file.title())
            delete_old_revs(file.title())


largeQuery = "select img_name from image where img_width > 600 or img_height > 600"

resize_and_upload(largeQuery)
