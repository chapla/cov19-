from django.shortcuts import render
import requests
import _strptime
import json
import codecs, json
import time
from datetime import datetime
from cov19 import models
import os
import pymysql
import selenium
from selenium import webdriver
from time import sleep
import pandas as pd

os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject4.settings'


# Create your views here.
def reptile(request):
    # 详情数据url
    details_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
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
            details.append({"update_time": update_time, "provinces_name": provinces_name, "city_name": city_name,
                            "value": [confirm, confirm_add, heal, dead]})
            # 累计确诊 较昨日增加 治愈 死亡
    print(details)
    # 已经插入数据
    #  id = 0
    #  for i in details:
    #      id += 1
    #      models.details.objects.create(id=id, update_time=i[0], province_name=i[1], city_name=i[2], confirm=i[3],
    #                                    confirm_add=i[4], heal=i[5], dead=i[6])
    # 查询全国数据
    conn = pymysql.Connect(host='localhost', port=3306, user='root', passwd='123456', db='cov19', charset='utf8')
    sql = "select province_name,sum(confirm),sum(confirm_add),sum(heal),sum(dead) from cov19_details where update_time=(select update_time from cov19_details order by update_time desc limit 1) group by province_name;"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    result1 = []
    for i in result:
        result1.append({"name": i[0], "value": [int(i[4]), int(i[2]), int(i[3]), int(i[1])]})

    # 各个市的数据出处理
    city = ['上海', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东',
            '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '北京', '天津', '重庆', '香港', '澳门', '台湾']

    result3 = []
    sum = 0
    for i in city:
        sql = "select city_name,confirm,confirm_add,heal,dead from cov19_details where province_name = '" + i + "';"
        cur.execute(sql)
        a = cur.fetchall()
        result3.append([])
        if i == '上海' or i == '北京':
            for i, j in zip(a, range(0, 34)):
                result3[sum].append({"name": i[0] + "区", "value": [int(i[1]), int(i[2]), int(i[3]), int(i[4])]})
        else:
            for i, j in zip(a, range(0, 34)):
                result3[sum].append({"name": i[0] + "市", "value": [int(i[1]), int(i[2]), int(i[3]), int(i[4])]})
        sum += 1

    # 折线图处理，获取日期
    data = []
    for i in history.keys():
        data.append(i)
    confirm = []
    suspect = []
    heal = []
    dead = []
    confirm_add = []
    suspect_add = []
    heal_add = []
    dead_add = []
    for i in history.items():
        confirm.append(i[1]['confirm'])
        suspect.append(i[1]['suspect'])
        heal.append(i[1]['heal'])
        dead.append(i[1]['dead'])
        confirm_add.append(i[1]['confirm_add'])
        suspect_add.append(i[1]['suspect_add'])
        heal_add.append(i[1]['heal_add'])
        dead_add.append(i[1]['dead_add'])
    today_data = str(confirm[-1]) + "      " + str(suspect[-1]) + "       " + str(heal[-1]) + "     " + str(dead[-1])

    # 词云 百度热搜
    # 设置无头浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    # 实例谷歌浏览器对象
    browser = webdriver.Chrome(
        executable_path=r'C:\Users\renyu\Downloads\浏览器\khjioh\chromedriver_win32\chromedriver.exe', options=options)
    url = "http://top.baidu.com/buzz/shijian.html"
    # get请求百度热搜榜url
    browser.get(url)
    tr = browser.find_elements_by_tag_name("tr")
    context = []
    # 获取每个热搜的标题以及对应的热度,并封装在字典中
    for i in range(2, len(tr) + 1):
        title = browser.find_element_by_xpath(
            '//table[@class="list-table"]/tbody/tr[' + str(i) + ']//td[@class="keyword"]').text
        heat = browser.find_element_by_xpath(
            '//table[@class="list-table"]/tbody/tr[' + str(i) + ']//td[@class="last"]').text
        context.append({"name": title, "value": int(heat)})
    browser.close()
    print(context)

    # 湖北迁徙图 百度迁徙大数据爬取 数据处理

    return render(request, 'map.html', {
        'result1': json.dumps(result1),
        'result3': json.dumps(result3),
        'data': json.dumps(data),
        'confirm': json.dumps(confirm),
        'suspect': json.dumps(suspect),
        'heal': json.dumps(heal),
        'dead': json.dumps(dead),
        'today_data': json.dumps(today_data),
        'confirm_add': json.dumps(confirm_add),
        'suspect_add': json.dumps(suspect_add),
        'heal_add': json.dumps(heal_add),
        'dead_add': json.dumps(dead_add),
        'context': json.dumps(context),

    })


# ----------------------------------------------------------------------------------------------------------------------------

# 中国当日疫情数据
def index(request):
    # 各省当日详情数据url
    details_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    # 中国历史数据url
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
        date = i['y'] + '.' + i['date']  # 时间
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
            details.append({"update_time": update_time, "provinces_name": provinces_name, "city_name": city_name,
                            "value": [confirm, confirm_add, heal, dead]})
            # 累计确诊 较昨日增加 治愈 死亡

    # 已经插入数据
    #  id = 0
    #  for i in details:
    #      id += 1
    #      models.details.objects.create(id=id, update_time=i[0], province_name=i[1], city_name=i[2], confirm=i[3],
    #                                    confirm_add=i[4], heal=i[5], dead=i[6])
    # 查询全国数据
    conn = pymysql.Connect(host='localhost', port=3306, user='root', passwd='123456', db='cov19', charset='utf8')
    sql = "select province_name,sum(confirm),sum(confirm_add),sum(heal),sum(dead) from cov19_details where update_time=(select update_time from cov19_details order by update_time desc limit 1) group by province_name;"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    result1 = []
    for i in result:
        result1.append({"name": i[0], "value": [int(i[4]), int(i[2]), int(i[3]), int(i[1])]})
    print(result1)
    # 各个市的数据出处理
    city = ['上海', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东',
            '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '北京', '天津', '重庆', '香港', '澳门', '台湾']

    result3 = []
    sum = 0
    for i in city:
        sql = "select city_name,confirm,confirm_add,heal,dead from cov19_details where province_name = '" + i + "';"
        cur.execute(sql)
        a = cur.fetchall()
        result3.append([])
        if i == '上海' or i == '北京':
            for i, j in zip(a, range(0, 34)):
                result3[sum].append({"name": i[0] + "区", "value": [int(i[1]), int(i[2]), int(i[3]), int(i[4])]})
        else:
            for i, j in zip(a, range(0, 34)):
                result3[sum].append({"name": i[0] + "市", "value": [int(i[1]), int(i[2]), int(i[3]), int(i[4])]})
        sum += 1

    # 折线图处理，获取日期
    confirm = []
    suspect = []
    heal = []
    dead = []
    confirm_add = []
    suspect_add = []
    heal_add = []
    dead_add = []
    for i in history.items():  # 以列表返回可遍历的(键, 值) 元组数组
        # ('2021-04-29', {'confirm': 103595, 'suspect': 10, 'heal': 98195, 'dead': 4857, 'confirm_add': 33, 'suspect_add': 3, 'heal_add': 22, 'dead_add': 0})
        confirm.append(i[1]['confirm'])
        suspect.append(i[1]['suspect'])
        heal.append(i[1]['heal'])
        dead.append(i[1]['dead'])
        confirm_add.append(i[1]['confirm_add'])
        suspect_add.append(i[1]['suspect_add'])
        heal_add.append(i[1]['heal_add'])
        dead_add.append(i[1]['dead_add'])
    today_data = str(confirm[-1]) + "      " + str(suspect[-1]) + "       " + str(heal[-1]) + "     " + str(dead[-1])

    return render(request, 'index.html', {
        'result1': json.dumps(result1),  # 个Python数据结构转换为JSON
        'result3': json.dumps(result3),
        'today_data': json.dumps(today_data),

    })


# 全国各省份历史疫情数据 时间轴
def time1(request):
    # 时间
    conn = pymysql.Connect(host='localhost', port=3306, user='root', passwd='123456', db='yiqing', charset='utf8')
    sql = "select data from privince where name='湖北'"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    result = list(result)
    datalist = []
    for i in result:
        datalist.append(i)
    datalist = datalist[20:30]

    # 对应时间的各省数据
    province = []
    for i in range(0, 10):
        sql = "select * from privince where data = '" + str(datalist[i][0]) + "';"
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        result = list(result)
        province.append([])
        for j in result:
            province[i].append({"name": j[15], "value": [int(j[4]), int(j[5]), int(j[3]), int(j[1])]})

    return render(request, 'history.html', {'province': json.dumps(province),
                                            'datalist': json.dumps(datalist),
                                            })


def move(request):
    city_name = []
    province_name = []
    value = []
    url = 'https://huiyan.baidu.com/migration/cityrank.jsonp?dt=province&id=420000&type=move_out&date=20210627&callback=jsonp_1624946987271_3443418'
    rq = requests.get(url)
    html = rq.content.decode('utf-8')
    # 2.从html中提取信息
    # 字符串预处理
    html1 = html[29:-1]
    data = json.loads(html1)['data']['list']
    print(data)
    for i in range(len(data)):
        city_name.append(data[i]['city_name'][0:2])  # 赋值给一个列表
        if str(data[i]['province_name']) == '黑龙江省':
            province_name.append(data[i]['province_name'][0:3])
        else:
            province_name.append(data[i]['province_name'][0:2])
        value.append(data[i]['value'])
        # 3.数据的本地存储
    move_out_data = pd.DataFrame({
        'move_out': city_name,
        'move_in': province_name,
        'value': value
    })
    move_out_data.to_excel('./hubei_move_out.xlsx')

    df = pd.read_excel('./hubei_move_out.xlsx')
    data = df.values
    move = []
    for i in data:
        move.append([{"name": '湖北'}, {"name": i[2], "value": i[3] * 10}])

    # 迁入
    city_name = []
    province_name = []
    value = []
    url = 'https://huiyan.baidu.com/migration/cityrank.jsonp?dt=province&id=420000&type=move_in&callback=jsonp_1624936525560_5471490'
    rq = requests.get(url)
    html = rq.content.decode('utf-8')
    # 2.从html中提取信息
    # 字符串预处理
    html1 = html[29:-1]
    data = json.loads(html1)['data']['list']
    for i in range(len(data)):
        city_name.append(data[i]['city_name'][0:2])  # 赋值给一个列表
        if str(data[i]['province_name']) == '黑龙江省':
            province_name.append(data[i]['province_name'][0:3])
        else:
            province_name.append(data[i]['province_name'][0:2])
        value.append(data[i]['value'])
        # 3.数据的本地存储
    move_out_data = pd.DataFrame({
        'city_name': city_name,
        'province_name': province_name,
        'value': value
    })
    move_out_data.to_excel('./hubei_move_in.xlsx')
    df = pd.read_excel('./hubei_move_in.xlsx')
    data = df.values
    move_in = []
    for i in data:
        move_in.append([{"name": '湖北'}, {"name": i[2], "value": i[3] * 10}])
    print(move_in)
    return render(request, 'move.html', {"HFData": json.dumps(move),
                                         "HFData1": json.dumps(move_in)})


def wordc(request):
    # 词云 百度热搜
    # 设置无头浏览器 selenium操作chrome浏览器需要有ChromeDriver驱动来协助。
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 浏览器不提供可视化页面
    options.add_argument('--disable-gpu')  ## 禁用GPU加速
    # 实例谷歌浏览器对象
    browser = webdriver.Chrome(
        executable_path=r'C:\Users\renyu\Downloads\浏览器\khjioh\chromedriver_win32\chromedriver.exe', options=options)
    url = "http://top.baidu.com/buzz/shijian.html"
    # get请求百度热搜榜url
    browser.get(url)
    tr = browser.find_elements_by_tag_name("tr")
    context = []
    # 获取每个热搜的标题以及对应的热度,并封装在字典中
    for i in range(2, len(tr) + 1):
        title = browser.find_element_by_xpath(
            '//table[@class="list-table"]/tbody/tr[' + str(i) + ']//td[@class="keyword"]').text
        if 'search' in title:
            title = title[:-6]
        heat = browser.find_element_by_xpath(
            '//table[@class="list-table"]/tbody/tr[' + str(i) + ']//td[@class="last"]').text
        context.append({"name": title, "value": int(heat)})
    browser.close()
    return render(request, 'wordcloud.html', {"context": json.dumps(context)})


# 中国疫情总数据的新增跟累计折线图
def line(request):
    history_url = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare'
    headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4350.7 Safari/537.36'
    # 将获取的详情数据json字符串转化成字典
    # key为data的json字符串转化成字典
    history_response = requests.get(history_url, headers)
    # 将历史数据json字符串转化成字典
    history_dic = json.loads(history_response.text)['data']
    history = {}
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
    print(history)
    # 折线图处理，获取日期
    data = []
    for i in history.keys():
        data.append(i)
    confirm = []
    suspect = []
    heal = []
    dead = []
    confirm_add = []
    suspect_add = []
    heal_add = []
    dead_add = []
    # 格式如下，所有用i[1]('2021-06-27', {'confirm': 118358, 'suspect': 1, 'heal': 107981, 'dead': 5478, 'confirm_add': 117, 'suspect_add': 1, 'heal_add': 0, 'dead_add': 9})
    for i in history.items():  # 返回可遍历的(键, 值) 元组数组。
        confirm.append(i[1]['confirm'])
        suspect.append(i[1]['suspect'])
        heal.append(i[1]['heal'])
        dead.append(i[1]['dead'])
        confirm_add.append(i[1]['confirm_add'])
        suspect_add.append(i[1]['suspect_add'])
        heal_add.append(i[1]['heal_add'])
        dead_add.append(i[1]['dead_add'])

    return render(request, 'line.html', {
        'data': json.dumps(data),
        'confirm': json.dumps(confirm),
        'suspect': json.dumps(suspect),
        'heal': json.dumps(heal),
        'dead': json.dumps(dead),
        'confirm_add': json.dumps(confirm_add),
        'suspect_add': json.dumps(suspect_add),
        'heal_add': json.dumps(heal_add),
        'dead_add': json.dumps(dead_add), })


def ranking(request):
    conn = pymysql.Connect(host='localhost', port=3306, user='root', passwd='123456', db='yiqing', charset='utf8')
    sql = "select *  from  top order by  total_confirm desc"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    name = []
    confirm = []
    for i in result:
        confirm.append(i[1])
        name.append(i[5])
    sql = "select *  from  top order by  total_heal desc"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    name_heal = []
    heal = []
    for i in result:
        heal.append(i[2])
        name_heal.append(i[5])
    sql = "select *  from  top order by  total_dead desc"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    name_dead = []
    dead = []
    for i in result:
        dead.append(i[3])
        name_dead.append(i[5])
    sql = "select *  from  top order by  today_confirm desc"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    name_con = []
    con = []
    for i in result:
        con.append(i[4])
        name_con.append(i[5])
    return render(request,'ranking.html', {'confirm':json.dumps(confirm[0:5]),
                                           'name':json.dumps(name[0:5]),
                                           'heal': json.dumps(heal[0:5]),
                                           'name_heal': json.dumps(name_heal[0:5]),
                                           'dead': json.dumps(dead[0:5]),
                                           'name_dead': json.dumps(name_dead[0:5]),
                                           'con': json.dumps(con[0:5]),
                                           'name_con': json.dumps(name_con[0:5])
                                           })

def world(request):

    return render(request, 'world.html')
