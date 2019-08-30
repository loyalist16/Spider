# -*- coding:utf8 -*-
import sys, os
now = os.path.dirname("__file__")  # 当前目录
last = os.path.abspath(os.path.join(now, os.path.pardir)) # 上一级目录
last_last = os.path.abspath(os.path.join(last, os.path.pardir)) # 上上一级目录
sys.path.append(last_last)

import settings
import csv, json
import time
import logging
import requests
from lxml.html import etree


BASE_PATH = settings.BASE_PATH # E:\workdir\Spider
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)

# Handler
handler = logging.FileHandler(BASE_PATH + '/logs/jinpeng_log/error.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 创建 jp 基本报价 csv表
jp_headers = ['起运港', '目的港', 'LINE', '船公司', '船司简称', '船期', '20底', '40底', '40HQ底', '起始日期', '供应商', '备注', '备注1']
file_name1 = BASE_PATH + '/result_file/jinpeng/jp-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name1,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(jp_headers)

# 船司代码mapping
with open(BASE_PATH +'/crawler/jinpeng/company.json', 'r', encoding='utf8') as f:
    companies = json.loads(f.read())

# 获取动态cookie
def get_cookie():
    url = "http://www.shflyingeagle.com/"

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        'Host': "www.shflyingeagle.com",
    }

    response = requests.request("GET", url, headers=headers)
    Cookie = '; '.join(['='.join(item) for item in response.cookies.items()])
    return Cookie

# 获取 form-data 字段
def get_data(Cookie):
    url = "http://www.shflyingeagle.com/yj/frmYj2.aspx"
    headers = {
        'Referer': "http://www.shflyingeagle.com/",
        'Host': "www.shflyingeagle.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        'Upgrade-Insecure-Requests': "1",
        'Cookie': Cookie
    }

    response = requests.request("GET", url, headers=headers)
    html = etree.HTML(response.text)
    # __EVENTTARGET = html.xpath('//*[@id="__EVENTTARGET"]/@value')[0]
    __EVENTARGUMENT = html.xpath('//*[@id="__EVENTARGUMENT"]/@value')[0]
    __VIEWSTATE = html.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
    __VIEWSTATEENCRYPTED = html.xpath('//*[@id="__VIEWSTATEENCRYPTED"]/@value')[0]
    __EVENTVALIDATION = html.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0]
    data = {
        "__EVENTARGUMENT": __EVENTARGUMENT,
        "__VIEWSTATE": __VIEWSTATE,
        "__VIEWSTATEENCRYPTED": __VIEWSTATEENCRYPTED,
        "__EVENTVALIDATION": __EVENTVALIDATION
    }
    return data

# 存储至csv文件中
def save2csv(List, filePath):
    with open(filePath, 'a+', newline='', encoding='utf8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(List)

# 获取详细信息
def get_message(line, result, flag):
    # 起始港
    origination = "SHANGHAI"
    # 目的港
    destination = result.xpath('./td[1]/span/text()')
    if destination:
        flag = destination = destination[0].strip()
    else:
        destination = flag
    # 船期
    schedule = result.xpath('./td[2]/span/text()')
    if schedule:
        schedule = schedule[0].strip()
    else:
        schedule = ''
    # 船司
    company = result.xpath('./td[3]/span/text()')[0].strip()
    if company in companies.keys():
        companyCode = companies.get(company)
    else:
        companyCode = company
    # 小箱
    GP20 = result.xpath('./td[4]/text()')[0].strip("↑ ) (")
    # 大箱
    GP40 = result.xpath('./td[5]/text()')[0].strip("↑ ) (")
    # 高箱
    HC40 = result.xpath('./td[6]/text()')[0].strip("↑ ) (")
    # LSS
    lss = result.xpath('./td[7]/text()')[0].strip()
    # 生效日
    date = result.xpath('./td[8]/text()')[0].strip()
    # 备注
    remark = result.xpath('./td[10]/span/text()')
    if remark:
        remark = remark[0].strip()
    else:
        remark = ''
    message = [origination, destination, line, company, companyCode, schedule, GP20, GP40, HC40, lss, date, remark]
    return message, flag

# 日本基航
def get_japan(line, result, flag):
    # 起始港
    origination = "SHANGHAI"
    # 船司
    company = result.xpath('./td[1]/span/text()')
    if company:
        flag = company = company[0].strip()
    else:
        company = flag

    if company in companies.keys():
        companyCode = companies.get(company)
    else:
        companyCode = company
    # 船期
    schedule = result.xpath('./td[2]/span/text()')
    if schedule:
        schedule = schedule[0].strip()
    else:
        schedule = ''
    # 目的港
    destination = result.xpath('./td[3]/span/text()')[0].strip()
    # 小箱
    GP20 = result.xpath('./td[4]/text()')[0].strip("↑ ) (")
    # 大箱
    GP40 = result.xpath('./td[5]/text()')[0].strip("↑ ) (")
    # 高箱
    HC40 = result.xpath('./td[6]/text()')[0].strip("↑ ) (")
    # LSS
    lss = result.xpath('./td[7]/text()')[0].strip()
    # 生效日
    date = result.xpath('./td[8]/text()')[0].strip()
    # 备注
    remark = result.xpath('./td[10]/span/text()')
    if remark:
        remark = remark[0].strip()
    else:
        remark = ''
    message = [origination, destination, line, company, companyCode, schedule, GP20, GP40, HC40, lss, date, remark]
    return message, flag

# 抓取
def crawl(Cookie, data):
    url = "http://www.shflyingeagle.com/yj/frmYj2.aspx"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Referer': "http://www.shflyingeagle.com/yj/frmYj2.aspx",
        'Host': "www.shflyingeagle.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        'Cookie': Cookie,
        'Origin': "http://www.shflyingeagle.com",
        }

    response = requests.request("POST", url, data=data, headers=headers)
    html = etree.HTML(response.text)
    # 航线
    line = html.xpath('//*[@id="lblTypeName"]/text()')[0]  # '东南亚线'
    # 内容
    results = html.xpath('//*[@id="dgdList"]/tr[@class="Row" or @class="AlternatingRow"]')
    return line, results

# 逻辑处理
def main(retry=3):
    try:
        Cookie = get_cookie()
        data = get_data(Cookie)
        for i in range(0, 12):
            target = "lnkHx" + str(i)
            data["__EVENTTARGET"] = target
            line, results = crawl(Cookie, data)
            flag = ''
            if line == '日本基港':
                for result in results:
                    message, flag = get_japan(line, result, flag)
                    save2csv(message, file_name1)
                logging.warning(f'{line}航线抓取完成')
            else:
                for result in results:
                    message, flag = get_message(line, result, flag)
                    save2csv(message, file_name1)
                logging.warning(f'{line}航线抓取完成')
    except:
        logger.error("错误详情：",exc_info=True)
        if retry > 0:
            logger.warning(f"正在尝试第{4-retry}次连接")
            retry -= 1
            time.sleep(1)
            return main(retry)
        else:
            logger.error("抓取失败")


if __name__ == "__main__":
    start = time.time()
    main()
    logger.critical(f"总耗时{time.time() - start}秒")