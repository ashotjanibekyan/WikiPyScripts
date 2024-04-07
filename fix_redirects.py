import pywikibot as pw
import toolforge

import helpers
from helpers import sql_to_matrix

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')

double_sql_query = '''SELECT src.page_namespace,
       src.page_title
FROM page AS src
JOIN redirect ON rd_from = src.page_id
JOIN page AS dbl ON dbl.page_namespace = rd_namespace
AND dbl.page_title = rd_title
WHERE dbl.page_is_redirect = 1;'''

broken_sql_query = '''SELECT page_namespace,
       page_title
FROM page AS src
JOIN redirect ON rd_from = src.page_id
WHERE rd_interwiki = ''
  AND NOT EXISTS
    (SELECT 1
     FROM page AS redir
     WHERE redir.page_namespace = rd_namespace
       AND redir.page_title = rd_title);'''


def get_target_or_none(page: pw.Page):
    if page.exists() and not page.isRedirectPage():
        return page
    if not page.exists():
        return get_target_or_none(page.moved_target())
    if page.isRedirectPage():
        return get_target_or_none(page.getRedirectTarget())


def fix_double_redirect(page: pw.Page):
    try:
        target = get_target_or_none(page)
        if target:
            page.text = f'#ՎԵՐԱՀՂՈՒՄ [[{target.title(with_ns=True)}]]'
            page.save('ուղղում եմ կրկնակի վերահղումները')
    except pw.exceptions.NoMoveTargetError:
        page.delete(reason='կոտրված վերահղում')
    except pw.exceptions.CircularRedirectError:
        pass


def fix_broken_redirect(page: pw.Page):
    try:
        target = get_target_or_none(page)
        if target:
            page.text = f'#ՎԵՐԱՀՂՈՒՄ [[{target.title(with_ns=True)}]]'
            page.save('ուղղում եմ կոտրված վերահղումը')
    except pw.exceptions.NoMoveTargetError:
        page.delete(reason='ջնջում եմ կոտրված վերահղումը', prompt=False)
    except pw.exceptions.CircularRedirectError:
        pass


double_data = sql_to_matrix('hywiki', double_sql_query)
for row in double_data:
    ns = row[0]
    title = row[1]
    page = pw.Page(hywiki, title if ns == 0 else f'{helpers.nsMap[ns]}:{title}')
    fix_double_redirect(page)

broken_data = sql_to_matrix('hywiki', broken_sql_query)
for row in broken_data:
    ns = row[0]
    title = row[1]
    page = pw.Page(hywiki, title if ns == 0 else f'{helpers.nsMap[ns]}:{title}')
    fix_broken_redirect(page)
