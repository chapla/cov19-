import requests
import json
import pandas as pd
city_name = []
province_name = []
value = []
url = 'https://huiyan.baidu.com/migration/cityrank.jsonp?dt=province&id=420000&type=move_out&date=20210627&callback=jsonp_1624857663852_6860018'
rq = requests.get(url)
html = rq.content.decode('utf-8')
    # 2.从html中提取信息
    # 字符串预处理
html1 = html[29:-1]
data = json.loads(html1)['data']['list']
for i in range(len(data)):
    city_name.append(data[i]['city_name'][0:2])  # 赋值给一个列表
    province_name.append(data[i]['province_name'][0:2])
    value.append(data[i]['value'])
    # 3.数据的本地存储
move_out_data = pd.DataFrame({
        'move_out': city_name,
        'move_in': province_name,
        'value': value
    })
move_out_data.to_excel('./hubei_move_out.xlsx')

import pandas as pd

df = pd.read_excel('./hubei_move_out.xlsx')
data=df.values
move=[]
for i in data:
    move.append([{"name":'湖北'},{"name":i[2],"value":i[3]*10}])
print(move)