import toolforge
import pywikibot as pw

hywiki = pw.Site('hy', 'wikipedia')

query = '''SELECT p1.page_title, p1.page_namespace
FROM   page AS p1 
WHERE  p1.page_title NOT LIKE"%/%" 
       AND p1.page_namespace IN (1, 5, 7, 9, 11, 13, 15, 101, 829) 
       AND NOT EXISTS (SELECT 1 
                       FROM   page AS p2 
                       WHERE  p2.page_namespace = p1.page_namespace - 1 
                              AND p1.page_title = p2.page_title)
       AND p1.page_id NOT IN (SELECT cl_from FROM categorylinks WHERE cl_to = 'Որբ_քննարկման_էջ');'''

conn = toolforge.connect('hywiki')

with conn.cursor() as cur:
    cur.execute(query)
    results = cur.fetchall()
    text = ''
    nsMap = {0: "", 1: "Քննարկում:", 2: "Մասնակից:", 3: "Մասնակցի քննարկում:", 4: "Վիքիպեդիա:",
             5: "Վիքիպեդիայի քննարկում:", 6: "Պատկեր:", 7: "Պատկերի քննարկում:", 8: "MediaWiki:",
             9: "MediaWiki քննարկում:", 10: "Կաղապար:", 11: "Կաղապարի քննարկում:", 12: "Օգնություն:",
             13: "Օգնության քննարկում:", 14: "Կատեգորիա:", 15: "Կատեգորիայի քննարկում:", 100: "Պորտալ:",
             101: "Պորտալի քննարկում:", 828: "Մոդուլ:", 829: "Մոդուլի քննարկում:", 2300: "Gadget:",
             2301: "Gadget talk:", 2302: "Gadget definition:", 2303: "Gadget definition talk:", -2: "Մեդիա:",
             -1: "Սպասարկող:"}
    for r in results:
        text += '\n#[[:' + nsMap[r[1]] + r[0].decode('utf-8') + ']] - [[:' + nsMap[r[1] - 1] + r[0].decode(
            'utf-8') + ']]'
    p = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/կասկածելի քննարկման էջեր')
    p.text = text
    p.save(summary='թարմացում', botflag=False)
