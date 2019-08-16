# -*- coding:utf8 -*-
# from download import NoProxy, Abuyun, Dashenip
import sys, os
now = os.path.dirname("__file__")  # 当前目录
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
handler = logging.FileHandler(BASE_PATH + '/logs/haiguang_log/error.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

lock = Lock()
download = NoProxy()   # 未使用代理IP
# download = Abuyun()   # 使用阿布云代理IP
# download = Dashenip()   # 使用大神的代理池


# 创建szhg基本报价 csv表
szhg_headers = ['id', '起运港', '目的港', '船公司', '目的港挂靠', '航线代码', 'LINE', '航程', '船期', '中转港', '港区', '20底', '40底', '40HQ底', '起始日期', '结束日期', '供应商', '备注', '备注1', '备注2']
file_name1 = BASE_PATH + '/result_file/haiguang/szhg-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name1,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(szhg_headers)

# 创建附加费表
surcharge_headers = ['id', '附加费', '币种', '20底', '40底', '40HQ底', '单票', '付款方式']
file_name2 = BASE_PATH + '/result_file/haiguang/szhg_surcharge-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name2,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(surcharge_headers)


url = "http://www.soshipping.cn/shining_services/freightfclweb/queryPage"
headers = {
    'Host': "www.soshipping.cn",
    'Origin': "http://www.soshipping.cn",
    'Referer': "http://www.soshipping.cn/shining_website/shiningCn/pages/freightfcl/freightfcl.html",
    "Cookie": "JSESSIONID=DD2203B5C0F1B9A9D23B273F70F1F61D; Hm_lvt_be428d21c1dbbdf23032893c76ac4c1a=1565580996,1565748919,1565840944; ec_im_local_status=0; CUSTOM_INVITE_CONTENT=; ec_invite_state=0; Hm_lpvt_be428d21c1dbbdf23032893c76ac4c1a=1565841023; ec_im_tab_num=1; ec_invite_state_time=1565841022989",
    "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoie1wiY29ublR5cGVcIjoyLFwic3lzVHlwZVwiOjIsXCJ1c2VySWRcIjoyODA5MyxcInVzZXJOYW1lXCI6XCIxNTIwMTg2OTY4NFwiLFwicGFzc3dvcmRcIjpudWxsLFwiZW1wbG95ZWVOb1wiOm51bGwsXCJoZWFkUGljXCI6bnVsbCxcIm5hbWVcIjpcIlBvdGF0b1wiLFwibmlja05hbWVcIjpcIlwiLFwicGxhdGZvcm1cIjpudWxsLFwicGhvbmVOdW1iZXJcIjpcIjE1MjAxODY5Njg0XCIsXCJjb21wYW55SWRcIjoxLFwiY29tcGFueU5hbWVcIjpcIuS4iua1t-azm-i_nOWbvemZhei0p-i_kOS7o-eQhuaciemZkOWFrOWPuFwiLFwiY29tcGFueUxldmVsXCI6bnVsbCxcImxvZ29cIjpudWxsLFwiY3VzdG9tZXJJZFwiOjM3NzI2LFwiZGVwdElkXCI6bnVsbCxcImRpcmVjdG9yRmxhZ1wiOm51bGwsXCJkaXJlY3RvckRlcHRMaXN0XCI6bnVsbCxcInN1YkRlcHRMaXN0XCI6bnVsbCxcInN1YkRlcHRMaXN0U3RyXCI6bnVsbCxcInVzZXJMZXZlbFwiOm51bGwsXCJ1c2VyVHlwZVwiOjAsXCJmY2xMZXZlbElkXCI6bnVsbCxcImNvZGVcIjpcIkhHVzAxNzc3NlwiLFwiY3NDb2RlXCI6bnVsbCxcInJvbGVJZHNcIjpudWxsLFwicGVybWlzc2lvbnNcIjpudWxsLFwidXNlclBvcnRMaXN0XCI6bnVsbCxcInVzZXJSb3V0ZUxpc3RcIjpudWxsLFwidXNlclNoaXBwaW5nTGlzdFwiOm51bGx9IiwiZXhwIjoyNTMzNzA3MzYwMDB9.yTuc3UEqOLOikdW-4q-n022FlmTcgdGj2KPUP0yxxr8"
}
# 需爬取的总页数
def get_totalPage():
    '''返回总页数'''
    # url = "http://www.soshipping.cn/shining_services/freightfclweb/queryPage"
    # headers = {
    #     'Host': "www.soshipping.cn",
    #     'Origin': "http://www.soshipping.cn",
    #     'Referer': "http://www.soshipping.cn/shining_website/shiningCn/pages/freightfcl/freightfcl.html",
    #     "Cookie": "JSESSIONID=DD2203B5C0F1B9A9D23B273F70F1F61D; Hm_lvt_be428d21c1dbbdf23032893c76ac4c1a=1565580996,1565748919,1565840944; ec_im_local_status=0; CUSTOM_INVITE_CONTENT=; ec_invite_state=0; Hm_lpvt_be428d21c1dbbdf23032893c76ac4c1a=1565841023; ec_im_tab_num=1; ec_invite_state_time=1565841022989",
    #     "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoie1wiY29ublR5cGVcIjoyLFwic3lzVHlwZVwiOjIsXCJ1c2VySWRcIjoyODA5MyxcInVzZXJOYW1lXCI6XCIxNTIwMTg2OTY4NFwiLFwicGFzc3dvcmRcIjpudWxsLFwiZW1wbG95ZWVOb1wiOm51bGwsXCJoZWFkUGljXCI6bnVsbCxcIm5hbWVcIjpcIlBvdGF0b1wiLFwibmlja05hbWVcIjpcIlwiLFwicGxhdGZvcm1cIjpudWxsLFwicGhvbmVOdW1iZXJcIjpcIjE1MjAxODY5Njg0XCIsXCJjb21wYW55SWRcIjoxLFwiY29tcGFueU5hbWVcIjpcIuS4iua1t-azm-i_nOWbvemZhei0p-i_kOS7o-eQhuaciemZkOWFrOWPuFwiLFwiY29tcGFueUxldmVsXCI6bnVsbCxcImxvZ29cIjpudWxsLFwiY3VzdG9tZXJJZFwiOjM3NzI2LFwiZGVwdElkXCI6bnVsbCxcImRpcmVjdG9yRmxhZ1wiOm51bGwsXCJkaXJlY3RvckRlcHRMaXN0XCI6bnVsbCxcInN1YkRlcHRMaXN0XCI6bnVsbCxcInN1YkRlcHRMaXN0U3RyXCI6bnVsbCxcInVzZXJMZXZlbFwiOm51bGwsXCJ1c2VyVHlwZVwiOjAsXCJmY2xMZXZlbElkXCI6bnVsbCxcImNvZGVcIjpcIkhHVzAxNzc3NlwiLFwiY3NDb2RlXCI6bnVsbCxcInJvbGVJZHNcIjpudWxsLFwicGVybWlzc2lvbnNcIjpudWxsLFwidXNlclBvcnRMaXN0XCI6bnVsbCxcInVzZXJSb3V0ZUxpc3RcIjpudWxsLFwidXNlclNoaXBwaW5nTGlzdFwiOm51bGx9IiwiZXhwIjoyNTMzNzA3MzYwMDB9.yTuc3UEqOLOikdW-4q-n022FlmTcgdGj2KPUP0yxxr8"
    # }
    response = download.post(url, headers, data={"pageNo":"1"})
    res = json.loads(response.text)
    totalPage = res.get('totalPage')
    logging.debug(f"总页数>>>{totalPage}")
    return int(totalPage)

# 每页的详细信息
def get_page_message(pageno):
    '''
    :param pageno: 当前页数 int
    :return: 详细信息 list，附加费data字段 list，附加费外键 list
    '''
    payload = {'pageNo':str(pageno)} # payload = "pageNo=1"
    response = download.post(url, headers, data=payload) # 使用通用下载模块得到请求
    logging.debug(f"第{pageno}页的状态>>>>{response.status_code}")
    if response.status_code == 200:
        if response.text:
            resp = response.text
            # logger.debug(f"第{pageno}页的详细信息>>>>{resp}")
            res = json.loads(resp)

            all_message_list = []  #存储所有的详细信息
            all_foreign_fileds =[]  #存储所有的外键字段
            all_foreign_keys = []  #存储所有的外键

            contents = res.get('rows')
            for content in contents:
                data = {}
                data['id'] = content.get('freightFclId')
                data['origination'] = content.get('portStartNameEn')
                data['destination'] = content.get('portEndNameEn')
                data['company'] = content.get('shippingName')
                data['port_of_call'] = content.get('portEndWharf')
                data['routeCode'] = content.get('routeCode')
                data['line'] = content.get('routeName')
                data['voyage'] = content.get('voyage')
                data['leaveday'] = content.get('schedule')
                data['transfer'] = content.get('transportNameEn')
                data['minato'] = content.get('wharfNameEn')
                data['GP20'] = content.get('price20')
                data['GP40'] = content.get('price40')
                data['HC40'] = content.get('price40hq')
                data['begindate'] = content.get('beginDateStr')
                data['enddate'] = content.get('endDateStr')
                data['supplier'] = content.get('supplierName')
                data['remark'] = content.get('remarkIn')
                data['remark1'] = content.get('remarkOut')
                data['remark2'] = content.get('descWeight')
                # print(f"data>>>>",data)
                all_message_list.append(data)

                surcharge_fields = {}
                surcharge_fields['portStartId'] = content.get('portStartId')
                surcharge_fields['portEndId'] = content.get('portEndId')
                surcharge_fields['shippingId'] = content.get('shippingId')
                surcharge_fields['routeId'] = content.get('routeId')
                surcharge_fields['companyId'] = content.get('companyId')
                surcharge_fields['pageNo'] = str(pageno)

                all_foreign_fileds.append(surcharge_fields)

                all_foreign_keys.append(content.get('freightFclId'))
                # print(content.get('freightFclId'))
            logging.info(f'第{pageno}页爬取完成')
            return all_message_list, all_foreign_fileds, all_foreign_keys
        else:
            return None, None ,None
    else:
        return None, None, None

# 附加费信息
def get_surcharge(surcharge_fields, freightFclId):
    '''
    :param surcharge_fields: 附加费data字段
    :param freightFclId: 附加费外键
    :return: 附加费详细信息
    '''
    url = "http://www.soshipping.cn/shining_services/freightfclweb/querysurchargefcl"
    payload = surcharge_fields
    # payload = "portStartId=1338&portEndId=174&shippingId=239&routeId=16&companyId=1&pageNo=1"
    response = download.post(url, headers, data=payload)
    if response.status_code == 200:
        if response.text:
            res = json.loads(response.text)
            surChargeList = res.get('surChargeList')

            need_surcharges = [] #需要的附加费列表

            for surCharges in surChargeList:
                surcharge = {}
                surcharge['freightFclId'] = freightFclId
                surcharge['chargeNameCode'] = surCharges.get('chargeNameCode')
                surcharge['currencyStr'] = surCharges.get('currencyStr')
                surcharge['price20'] = surCharges.get('price20')
                surcharge['price40'] = surCharges.get('price40')
                surcharge['price40hq'] = surCharges.get('price40hq')
                surcharge['billPrice'] = surCharges.get('billPrice')
                surcharge['payTypeStr'] = surCharges.get('payTypeStr')

                need_surcharges.append(surcharge)
            return need_surcharges
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

    all_message_list, all_foreign_fileds, all_foreign_keys = get_page_message(pageNo)
    # print("all_message_list>>>",all_message_list)
    if all_message_list:
        for message in all_message_list:
            lock.acquire()
            save2mysql(message, 'szhg')
            save2csv(message, file_name1)
            lock.release()

        for i in range(len(all_foreign_keys)):
            surcharges = get_surcharge(all_foreign_fileds[i], all_foreign_keys[i])
            if surcharges:
                for surcharge in surcharges:
                    lock.acquire()
                    save2mysql(surcharge, 'szhg_surcharge')
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

if __name__ == '__main__':
    start = time.time()
    main()
    logger.info(f"总耗时{time.time()-start}秒")