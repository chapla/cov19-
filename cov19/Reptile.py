import requests
import json
import time

#腾讯   爬取全国历史数据    各省最新数据
# 详情数据url
details_url = ' https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    # 历史数据url
history_url = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare'
headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4350.7 Safari/537.36'
details_response = requests.get(details_url, headers)
    # 将获取的详情数据json字符串转化成字典
details_json = json.loads(details_response.text)
    # key为data的json字符串转化成字典
details_dic = json.loads(details_json['data'])
history_response = requests.get(history_url, headers)
    # 将历史数据json字符串转化成字典
history_dic = json.loads(history_response.text)['data']
history = {}
details = []
    # 将历史数据保存
for i in history_dic['chinaDayList']:
    date = i['y'] + '.' + i['date']
    tup = time.strptime(date, '%Y.%m.%d')
        # 改变时间格式不然插入数据时数据库会报错
    date = time.strftime('%Y-%m-%d', tup)
    confirm = i['confirm']
    suspect = i['suspect']
    dead = i['dead']
    heal = i['heal']
    history[date] = {"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}
    # 将历史当天新增数据保存
for i in history_dic['chinaDayAddList']:
    date = i['y'] + '.' + i['date']
    tup = time.strptime(date, '%Y.%m.%d')
    date = time.strftime('%Y-%m-%d', tup)
    confirm = i['confirm']
    suspect = i['suspect']
    dead = i['dead']
    heal = i['heal']
    history[date].update({"confirm_add": confirm, "suspect_add": suspect, "heal_add": heal, "dead_add": dead})

update_time = details_dic['lastUpdateTime']
data_countries = details_dic['areaTree']
    # 获取省级数据列表
data_provinces = data_countries[0]['children']
    # 将详情数据保存
for pro_info in data_provinces:
    provinces_name = pro_info['name']
    for city_info in pro_info['children']:
        city_name = city_info['name']
        confirm = city_info['total']['confirm']
        confirm_add = city_info['today']['confirm']
        heal = city_info['total']['heal']
        dead = city_info['total']['dead']
        details.append({"update_time":update_time, "provinces_name":provinces_name, "city_name":city_name, "confirm":confirm, "confirm_add":confirm_add, "heal":heal, "dead":dead})
        # 累计确诊 较昨日增加 治愈 死亡
print(type(history))

