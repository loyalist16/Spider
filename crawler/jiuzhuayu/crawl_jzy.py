# -*- coding:utf8 -*-
import sys, os
now = os.path.dirname(__file__)  # 当前目录
last = os.path.abspath(os.path.join(now, os.path.pardir)) # 上一级目录
last_last = os.path.abspath(os.path.join(last, os.path.pardir)) # 上上一级目录
sys.path.append(last_last)

import settings
from multiprocessing import Pool, Lock
import json
import csv
import pymysql
import time
import logging
from config.download import NoProxy, Abuyun, Dashenip


BASE_PATH = settings.BASE_PATH # E:\workdir\Spider
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)

# Handler
handler = logging.FileHandler(BASE_PATH + '/logs/jiuzhuayu_log/error.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

lock = Lock()
download = NoProxy()   # 未使用代理IP


# 航线名称
with open(BASE_PATH + '/crawler/jiuzhuayu/' + 'endport_route.json', 'r', encoding='utf8') as f:
    routes = json.loads(f.read())

url = "http://www.cn956.com/club9/freight/editFreight.php"
headers = {
    'X-Requested-With': "XMLHttpRequest",
    'Content-Type': "application/x-www-form-urlencoded",
    'Host': "www.cn956.com",
    'Origin': "http://www.cn956.com",
    }
data = {"page":'1',
        "pagesize":'50',
        'stport':'CNSHA',
        'ifreight':'ifreight'}
querystring = {"actioncode":"getsolutionlist","myusernm":""}

# 创建 jzy 基本报价 csv表
jp_headers = ['id', '起运港', '目的港', '船公司', '目的港挂靠', '航线代码', 'LINE', '航程', '船期', '中转港', '港区', '20底', '40底', '40HQ底', '起始日期', '结束日期', '供应商', '备注', '备注1', '备注2']
file_name1 = BASE_PATH + '/result_file/jiuzhuayu/jzy-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name1,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(jp_headers)

# 创建附加费表
surcharge_headers = ['id', '附加费代码', '附加费名称', '船司', '航线', '起运港', '目的港', '币种', '20底', '40底', '40HQ底', '单票', '付款方式']
file_name2 = BASE_PATH + '/result_file/jiuzhuayu/jzy_surcharge-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name2,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(surcharge_headers)

# 总页数
def get_totalPage():
    """
    总页数 str
    :return:
    """
    response = download.post(url, headers=headers, data=data, params=querystring)
    res = json.loads(response.text)
    return res.get('pageCount')

# 每页的详细信息
def get_messages(pageno):
    '''
    :param pageno:当前页数 int
    :return: 详细信息 list，附加费data字段 list，附加费外键 list
    '''
    data = {"page": str(pageno),
            "pagesize": '50',
            'stport': 'CNSHA',
            'ifreight': 'ifreight'}
    response = download.post(url, headers=headers, data=data, params=querystring)
    if response.text:
        res = json.loads(response.text)
        contents = res.get('result') # 所有结果集合

        all_message_list = []  # 存储所有的详细信息
        all_foreign_fileds = []  # 存储所有的外键字段
        all_surcharge_needs = []  # 存储附加费字段所需的字段

        for content in contents:
            data = {}
            data['id'] = content.get('newfreight_id')
            data['origination'] = content.get('ss_stport')
            data['destination'] = content.get('ss_endport')
            data['company'] = content.get('chsnm')
            data['port_of_call'] = content.get('ss_anchport')
            data['routeCode'] = None
            data['line'] = routes.get(content.get('ss_endport'))
            data['voyage'] = content.get('ss_voyage')
            data['schedule'] = content.get('ss_schedule')
            data['transfer'] = content.get('ss_transport')
            data['minato'] = content.get('portarea_id')
            data['GP20'] = content.get('ss_20pr')
            data['GP40'] = content.get('ss_40pr')
            data['HC40'] = content.get('ss_40hq')
            data['startdate'] = content.get('ss_efdate')
            data['enddate'] = content.get('ss_enddate')
            data['supplier'] = '九爪鱼'
            data['remark'] = content.get('ss_memo')
            data['remark1'] = None
            data['remark2'] = None
            # print(f"data>>>>",data)
            all_message_list.append(data)

            surcharge_needs = {}
            surcharge_needs['company'] = content.get('chsnm')
            surcharge_needs['origination'] = content.get('ss_stport')
            surcharge_needs['destination'] = content.get('ss_endport')
            surcharge_needs['line'] = routes.get(content.get('ss_endport'))

            all_surcharge_needs.append(surcharge_needs)

            surcharge_fields = {}
            surcharge_fields['actioncode'] = 'getstartdate'
            surcharge_fields['ss_schedule'] = content.get('ss_schedule')
            surcharge_fields['efdate'] = time.strftime('%Y', time.localtime(time.time())) + '-' + content.get('ss_efdate')
            surcharge_fields['enddate'] = '-'
            surcharge_fields['newfreight_id'] = content.get('newfreight_id')

            all_foreign_fileds.append(surcharge_fields)

        return all_message_list, all_surcharge_needs, all_foreign_fileds
    else:
        return None, None, None


def get_surcharge(foreign_fileds, surcharge_needs):
    response = download.post(url, headers=headers, params=foreign_fileds, data=None)
    if response.text:
        contents = json.loads(response.text).get('result').get('listplusefee')
        if contents:
            all_surcharges = []  # 需要的附加费列表

            for content in contents:
                surcharge = {}
                surcharge['freightFclId'] = foreign_fileds.get('newfreight_id')
                surcharge['chargeNameCode'] = content.get('ec_egnm')
                surcharge['chargeName'] = content.get('ec_chnm')
                surcharge['company'] = surcharge_needs.get('company')
                surcharge['line'] = surcharge_needs.get('line')
                surcharge['origination'] = surcharge_needs.get('origination')
                surcharge['destination'] = surcharge_needs.get('destination')
                surcharge['currencyStr'] = content.get('currency_id')
                surcharge['price20'] = content.get('eci_rc20')
                surcharge['price40'] = content.get('eci_rc40')
                surcharge['price40hq'] = content.get('eci_rc40hq')
                surcharge['billPrice'] = content.get('svrc')
                surcharge['payTypeStr'] = None

                all_surcharges.append(surcharge)
            return all_surcharges
        else:
            return None

# 存储至MySQL中
def save2mysql(data, table):
    '''
    :param data: 需存储的信息，字典格式
    :param table: 需存储的表名
    :return: 空
    '''
    db = pymysql.connect(host = 'localhost', user='root', password='123456', port= 3306, db= 'szfy')
    cursor = db.cursor()
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))

    # sql = "INSERT INTO {table}({keys})VALUES({values})".format(table=table,keys=keys,values=values)
    sql = "INSERT INTO {table}({keys})VALUES({values})ON DUPLICATE KEY UPDATE ".format(table=table, keys=keys,
                                                                                       values=values)
    update = ','.join([" {key} = %s".format(key=key) for key in data])
    sql += update
    try:
        if cursor.execute(sql, tuple(data.values()) * 2):
            # print("successful")
            db.commit()
    except:
        print("failed")
        logger.error("It's an Error:", exc_info=True)
        db.rollback()
    db.close()

# 存储至csv文件中
def save2csv(data, filePath):
    with open(filePath, 'a+', newline='', encoding='utf8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(list(data.values()))

# 抓取逻辑
def crawl(pageNo):

    all_message_list, all_surcharge_needs, all_foreign_fileds = get_messages(pageNo)
    # print("all_message_list>>>",all_message_list)
    if all_message_list:
        for message in all_message_list:
            lock.acquire()
            save2mysql(message, 'jzy')
            save2csv(message, file_name1)
            lock.release()

        for i in range(len(all_foreign_fileds)):
            surcharges = get_surcharge(all_foreign_fileds[i], all_surcharge_needs[i])
            if surcharges:
                for surcharge in surcharges:
                    lock.acquire()
                    save2mysql(surcharge, 'jzy_surcharge')
                    save2csv(surcharge, file_name2)
                    lock.release()
    else:
        logger.error(f"第{pageNo}页爬取失败")

# 执行
def main():

    pool = Pool(processes=4)
    totalPage = get_totalPage()
    # totalPage = 10

    for pageNO in range(1,totalPage+1):
        time.sleep(0.5)
        pool.apply_async(crawl, (pageNO,))

    pool.close()
    pool.join()

if __name__ == "__main__":
    start = time.time()
    main()
    logger.critical(f"总耗时{time.time()-start}秒")