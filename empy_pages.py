import toolforge
import pywikibot as pw
from helpers import nsMap

conn = toolforge.connect('hywiki')
hywiki = pw.Site('hy', 'wikipedia')


sql = 'SELECT page_title, page_namespace FROM page WHERE page_len = 0 AND page_namespace != 2 and page_namespace != 3;'

with conn.cursor() as cur:
    text = 'Ցանկում ներառված են Հայերեն Վիքիպեդիայի բոլոր դատարկ էջերը՝ բացառությամբ այն էջերը, որոնք մասնակից մասնակցի քննարկում անվանատարածքներում են։\n'
    cur.execute(sql)
    results = cur.fetchall()
    for r in results:
        text += f"# [[{nsMap[r[1]]}:{r[0].decode('utf-8')}\n"

    page = pw.Page(hywiki, "Մասնակից:ԱշոտՏՆՂ/ցանկեր/դատարկ էջեր")
    page.text = text
    page.save("թարմացում")