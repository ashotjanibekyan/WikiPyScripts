import datetime

import toolforge
import pywikibot as pw
from pywikibot.data import api

import helpers

hywiki: pw.Site = pw.Site('hy', 'wikipedia')

gen = hywiki._generator(api.ListGenerator, type_arg='allusers',
                        auprop='editcount|groups|registration',
                        auactiveusers=True,
                        aufrom='!', total=None)

sql_template = '''WITH mymonths AS
  (SELECT DISTINCT DATE_FORMAT(DATE_ADD('2004-04-07', INTERVAL (t4*10000 + t3*1000 + t2*100 + t1*10 + t0) DAY), '%%Y-%%m-%%d') AS mymonths_month
   FROM
     (SELECT 0 AS t0
      UNION SELECT 1
      UNION SELECT 2
      UNION SELECT 3
      UNION SELECT 4
      UNION SELECT 5
      UNION SELECT 6
      UNION SELECT 7
      UNION SELECT 8
      UNION SELECT 9) AS t0,

     (SELECT 0 AS t1
      UNION SELECT 1
      UNION SELECT 2
      UNION SELECT 3
      UNION SELECT 4
      UNION SELECT 5
      UNION SELECT 6
      UNION SELECT 7
      UNION SELECT 8
      UNION SELECT 9) AS t1,

     (SELECT 0 AS t2
      UNION SELECT 1
      UNION SELECT 2
      UNION SELECT 3
      UNION SELECT 4
      UNION SELECT 5
      UNION SELECT 6
      UNION SELECT 7
      UNION SELECT 8
      UNION SELECT 9) AS t2,

     (SELECT 0 AS t3
      UNION SELECT 1
      UNION SELECT 2
      UNION SELECT 3
      UNION SELECT 4
      UNION SELECT 5
      UNION SELECT 6
      UNION SELECT 7
      UNION SELECT 8
      UNION SELECT 9) AS t3,

     (SELECT 0 AS t4
      UNION SELECT 1
      UNION SELECT 2
      UNION SELECT 3
      UNION SELECT 4
      UNION SELECT 5
      UNION SELECT 6
      UNION SELECT 7
      UNION SELECT 8
      UNION SELECT 9) AS t4
   WHERE DATE_ADD('2004-04-07', INTERVAL (t4*10000 + t3*1000 + t2*100 + t1*10 + t0) DAY) <= NOW()),
     editsbymonth AS
  (SELECT DATE_FORMAT(STR_TO_DATE(CAST(rev_timestamp AS CHAR), '%%Y%%m%%d%%H%%i%%s'), '%%Y-%%m-%%d') AS editsbymonth_month,
          COUNT(*) AS C
   FROM revision_userindex
   JOIN actor ON rev_actor = actor_id
   WHERE actor_name = %s
   GROUP BY editsbymonth_month)
SELECT COALESCE(C, 0) AS Cc,
       mymonths_month,
       DATEDIFF(NOW(), mymonths_month) days
FROM editsbymonth
RIGHT JOIN mymonths ON mymonths_month = editsbymonth_month
HAVING Cc = 0
ORDER BY mymonths_month DESC
LIMIT 1'''

user_data = [['Մասնակից', 'Վերջին անգամ չի խմբագրել', 'Քանի՞ օր է անդադար խմբագրել']]
for user in gen:
    sql = sql_template
    conn = toolforge.connect('hywiki')
    with conn.cursor() as cur:
        cur.execute(sql, ((str(user['name']), )))
        results = cur.fetchall()
        for r in results:
            if r[2] == 0:
                continue
            user_data.append([user['name'], r[1], r[2]])

hywiki = pw.Page(hywiki, 'Վիքիպեդիա:Ցանկեր/խմբագիրներ ըստ անդադար խմբագրման օրերի')
hywiki.text = helpers.matrix_to_wikitable(user_data)
hywiki.save('թարմացում')
