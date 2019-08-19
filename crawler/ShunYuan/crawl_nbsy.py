# -*- coding:utf8 -*-

import sys, os
now = os.path.dirname(__file__)  # 当前目录
last = os.path.abspath(os.path.join(now, os.path.pardir)) # 上一级目录
last_last = os.path.abspath(os.path.join(last, os.path.pardir)) # 上上一级目录
sys.path.append(last_last)

import settings
from multiprocessing import Pool,Lock
import json
import csv, time
from config.download import Abuyun, NoProxy, Dashenip
import pymysql
import logging

BASE_PATH = settings.BASE_PATH # E:\workdir\Spider

# 通用代理IP 下载模块
# download = Download()
# 通用无代理IP 下载模块
download = NoProxy()
# 使用大神给的IP池
# download = Dashenip()
lock = Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# handler
handler = logging.FileHandler(BASE_PATH + '/logs/shunyuan_log/error.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# 创建nbsy基本报价 csv表
nbsy_headers = ['id', '起运港', '目的港', '船公司', '目的港挂靠', '航线代码', 'LINE', '航程', '船期', '中转港', '港区', '20底', '40底', '40HQ底', '起始日期', '结束日期', '供应商', '备注', '备注1', '备注2']
file_name1 = BASE_PATH + '/result_file/shunyuan/nbsy-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name1,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(nbsy_headers)

# 创建附加费表
surcharge_headers = ['id', '附加费代码', '附加费名称', '船司', '航线', '起运港', '目的港', '单位', '币种', '20底', '40底', '40HQ底', '单票']
file_name2 = BASE_PATH + '/result_file/shunyuan/nbsy_surcharge-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name2,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(surcharge_headers)

# 每条航线的所有信息
def get_all_messages(startPortCode, endPortCode):
    '''
    :param startPortCode: 起点
    :param endPortCode: 终点
    :return: html
    '''
    url = "http://www.51safround.com/page-web/searchFreight.html"

    querystring = {"nowPage": "1", "number": "100", "startPortCode": startPortCode, "endPortCode": endPortCode,
                   "num": "3"}

    headers = {
        'Cookie': "JSESSIONID=BDAE16D3BDD7CC3F418E10BBDC0D8F9F; name=1; chatsize=0; UM_distinctid=16c3d128203468-07cb5cd4700f21-3a65420e-144000-16c3d12820433b; growth=; offline=; JSESSIONID=69B5F2297B94D91C13BBDAF5DC47A357; CNZZDATA1273593192=1237074893-1564390852-https%253A%252F%252Fwww.baidu.com%252F%7C1564476713; twoHoursLaterAppear=true; WC_UID=9481; WC_JUID=9481-a3412a04edfe4376bbd1313ea1d4cdbc; USER_NAME=19979648720; USER_TYPE=0; COMCODE=8800; COMCODE_STATUS=0; NICK_NAME=loyal; ENABLE_PRICE=1; logined=false; Hm_lvt_6915824c43dd7788f9885b736a05d5a1=1564392844,1564450362,1564477124,1564477153; indexSearch=; Hm_lpvt_6915824c43dd7788f9885b736a05d5a1=1564477613,JSESSIONID=BDAE16D3BDD7CC3F418E10BBDC0D8F9F; name=1; chatsize=0; UM_distinctid=16c3d128203468-07cb5cd4700f21-3a65420e-144000-16c3d12820433b; growth=; offline=; JSESSIONID=69B5F2297B94D91C13BBDAF5DC47A357; CNZZDATA1273593192=1237074893-1564390852-https%253A%252F%252Fwww.baidu.com%252F%7C1564476713; twoHoursLaterAppear=true; WC_UID=9481; WC_JUID=9481-a3412a04edfe4376bbd1313ea1d4cdbc; USER_NAME=19979648720; USER_TYPE=0; COMCODE=8800; COMCODE_STATUS=0; NICK_NAME=loyal; ENABLE_PRICE=1; logined=false; Hm_lvt_6915824c43dd7788f9885b736a05d5a1=1564392844,1564450362,1564477124,1564477153; indexSearch=; Hm_lpvt_6915824c43dd7788f9885b736a05d5a1=1564477613; JSESSIONID=0A997513D9AC091114618A0C7681C38D",
        'Host': "www.51safround.com",
        'Referer': "http://www.51safround.com/page-web/search.html?nowPage=1&number=100&startPortCode=CNTAZ&endPortCode=USATL&num=3",
        }

    # 使用代理IP
    # response = self.universal.get(url, headers=headers, params=querystring)
    # 未使用代理IP
    response = download.get(url, headers=headers, params=querystring)
    logging.info(f"starting: {startPortCode}-{endPortCode}")
    return response

# 拿到报价信息
def get_public_price(response):
    '''
    返回当前航线 详细信息列表page_message_list，以及附加费外键Id列表 foreign_list
    '''
    if response.status_code == 200:
        if response.text:
            jsonDict = json.loads(response.text)
            contents = jsonDict.get('freighList')

            page_message_list = []   # 整页信息列表
            foreign_list = []   # 当前页面外键列表
            all_surcharge_needs = []  # 存储附加费字段所需的字段

            if contents:
                for content in contents:
                    data = {}
                    data['id'] = content.get('id')
                    data['origination'] = content.get('start_port_en')
                    data['destination'] = content.get('dest_port_en')
                    data['company'] = content.get('carrier')
                    data['port_of_call'] = content.get('endport_pier')
                    data['routeCode'] = content.get('searoute_code')
                    data['line'] = content.get('carrier_sealine')
                    data['voyage'] = content.get('sailtime')
                    data['schedule'] = content.get('weekCycle')
                    data['transfer'] = content.get('transferport_en')
                    data['minato'] = content.get('pier_en')
                    data['GP20'] = content.get('internetsellprice_20gp')
                    data['GP40'] = content.get('internetsellprice_40gp')
                    data['HC40'] = content.get('internetsellprice_40hq')
                    data['startdate'] = content.get('bottomStartTime')
                    data['enddate'] = content.get('bottomEenTime')
                    data['supplier'] = '顺圆'
                    data['remark'] = content.get('d_remark_in')
                    data['remark1'] = content.get('d_remark_out')
                    data['remark2'] = content.get('desc_weight')

                    surcharge_needs = {}
                    surcharge_needs['company'] = content.get('carrier')
                    surcharge_needs['origination'] = content.get('start_port_en')
                    surcharge_needs['destination'] = content.get('dest_port_en')
                    surcharge_needs['line'] = content.get('carrier_sealine')

                    all_surcharge_needs.append(surcharge_needs)

                    page_message_list.append(data)
                    foreign_list.append(data['id'])
                return page_message_list, foreign_list, all_surcharge_needs
            else:
                return None,None
        else:
            return None, None
    else:
        return None, None

# 拿到附加费信息
def get_surcharge(foreign_key, surcharge_needs):
    '''
    当前航线的附加费列表 line_surcharge_list
    '''
    url = "http://www.51safround.com/page-web/getJFreightAddItem.html"

    payload = {'jf_id': str(foreign_key)}
    headers = {
        'Cookie': "JSESSIONID=5DD8D863DD825A244EF3A63DB28D6F88; chatsize=0; UM_distinctid=16c6f266da639c-0d7b6b46b31c37-7373e61-1fa400-16c6f266da9549; JSESSIONID=DB2BCE81E1D8A580839CE0AA029E4D50; Hm_lvt_6915824c43dd7788f9885b736a05d5a1=1565232886; growth=; offline=; WC_UID=9481; WC_JUID=9481-16e5c5eebee14b868b978a3989d9c757; USER_NAME=19979648720; USER_TYPE=0; COMCODE=8800; COMCODE_STATUS=0; NICK_NAME=loyal; ENABLE_PRICE=1; logined=false; CNZZDATA1273593192=1436040615-1565232884-https%253A%252F%252Fwww.baidu.com%252F%7C1565261551; Hm_lpvt_6915824c43dd7788f9885b736a05d5a1=1565263312; indexSearch=http%3A%2F%2Fwww.51safround.com%2Fpage-web%2Fsearch.html%3FnowPage%3D1%26startPortCode%3DCNXMN%26endPortCode%3DUSATL%26num%3D3",
        'Host': "www.51safround.com",
        'Origin': "http://www.51safround.com",
        'Proxy-Connection': "keep-alive",
        'Referer': "http://www.51safround.com/page-web/search.html?nowPage=1&startPortCode=CNSHA&endPortCode=USATL&num=3&",
        }
    # 使用代理IP
    # response = self.universal.get(url, headers=headers, params=querystring)
    # 未使用代理IP
    response = download.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        if response.text:
            jsonDict = json.loads(response.text)
            surChargeList = jsonDict.get('list')
            # 当前航线的附加费列表
            line_surcharge_list = []
            for surCharges in surChargeList:
                surcharge = {}
                surcharge['freightFclId'] = foreign_key
                surcharge['chargeNameCode'] = surCharges.get('cost_code')
                surcharge['chargeName'] = surCharges.get('cost_name')
                surcharge['company'] = surcharge_needs.get('company')
                surcharge['line'] = surcharge_needs.get('line')
                surcharge['origination'] = surcharge_needs.get('origination')
                surcharge['destination'] = surcharge_needs.get('destination')
                surcharge['unit'] = surCharges.get('unit')
                surcharge['currencyStr'] = surCharges.get('currency_code')
                surcharge['price20'] = surCharges.get('price_20gp')
                surcharge['price40'] = surCharges.get('price_40gp')
                surcharge['price40hq'] = surCharges.get('price_40hq')
                surcharge['price_single'] = surCharges.get('price_single')

                line_surcharge_list.append(surcharge)
            return line_surcharge_list
        else:
            return None
    else:
        return None

# 存储至MySQL中
def save2mysql(data, table):
    '''
    :param data: 需存储的信息，字典格式
    :param table: 需存储的表名
    :return: 空
    '''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='szfy')
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
        logger.error("failed")
        logger.error("Error:", exc_info=True)
        db.rollback()
    db.close()

# 存储至csv文件中
def save2csv(data, filePath):
    with open(filePath, 'a+', newline='', encoding='utf8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(list(data.values()))

# 爬取逻辑
def crawler(startPortCode, endPortCode):

    response = get_all_messages(startPortCode, endPortCode)
    page_message_list, foreign_list, all_surcharge_needs = get_public_price(response)
    if page_message_list:
        lock.acquire()
        for page_message in page_message_list:
            logger.info(page_message)
            # lock.acquire()
            save2mysql(page_message, 'nbsy')
            save2csv(page_message, file_name1)
        lock.release()

        for foreign, surcharge_needs in zip(foreign_list, all_surcharge_needs):

            line_surcharge_list = get_surcharge(foreign, surcharge_needs)
            lock.acquire()
            for line_surcharge in line_surcharge_list:
                # lock.acquire()
                save2mysql(line_surcharge, 'nbsy_surcharge')
                save2csv(line_surcharge, file_name2)
            lock.release()
    else:
        logging.info(f"此航线暂无数据{startPortCode}-{endPortCode}")


def run():

    pool = Pool(processes=6)

    # 在windows上运行
    # with open("all_end_port.json", 'r', encoding='utf8') as f:
    #     strings = f.read()

    # 在linux上运行
    with open("workdir/Spider/crawler/ShunYuan/all_end_port.json", 'r', encoding='utf8') as f:
        strings = f.read()

    all_lines = json.loads(strings)
    startports = [i for i in all_lines.keys()]
    for startPortCode in startports:
        endports = all_lines.get(startPortCode)
        for endport in endports:
            endPortCode = endport.get('port_code')
            pool.apply_async(crawler, (startPortCode, endPortCode,))
            # pool.apply(self.test, (startPortCode, endPortCode,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    start_time = time.time()
    run()
    logger.critical(f"共耗时{time.time()-start_time}秒")

