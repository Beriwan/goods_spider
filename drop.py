import re

import pymysql

db=pymysql.connect(host='10.10.0.125', user='root',
                                      password='5560203@wstSpider!', db='taobao_live', port=3306, charset='utf8')
cur=db.cursor()
id_list = []
id_set = ()
with open('D:\\work\\goods_spider\\error_0612.txt','r') as f:
    for item in f.readlines():
        try:
            id = re.search('\?id=(\d+)',item.strip()).group(1)
            sql = 'replace into `source_taobao_live_itemId_drop` (itemId) values (%s)'
            cur.execute(sql,id)
            print(id)
            # id_list.append(tuple(id))
        except Exception as e:
            # print(e)
            continue
    db.commit()
    cur.close()
    db.close()