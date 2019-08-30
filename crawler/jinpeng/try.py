import requests
from lxml.html import etree


# 创建 jp 基本报价 csv表
szhg_headers = ['起运港', '目的港', 'LINE', '船公司', '船期', '20底', '40底', '40HQ底', '起始日期', '供应商', '备注', '备注1']
file_name1 = BASE_PATH + '/result_file/jiuzhuayu/jzy-' + time.strftime("%Y-%m-%d",time.localtime()) + '.csv'
with open(file_name1,'w', newline='', encoding='utf8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(szhg_headers)

def get_cookie():
    url = "http://www.shflyingeagle.com/"

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        'Host': "www.shflyingeagle.com",
        }

    response = requests.request("GET", url, headers=headers)
    Cookie = '; '.join(['='.join(item) for item in response.cookies.items()])
    return Cookie

# 获取form-data字段
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


def get_messages(Cookie, data):
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
    line = html.xpath('//*[@id="lblTypeName"]/text()')  # ['东南亚线']
    # 内容
    results = html.xpath('//*[@id="dgdList"]/tr[@class="Row" or @class="AlternatingRow"]')
    # 目的港
    flag = results[0].xpath('./td//text()')[1]
    for i in range(len(results)):
        List = results[i].xpath('./td//text()')
        result = []
        for j in range(len(List)):
            List[j] = List[j].strip()
            if j >= 2:
                if List[j]:
                    result.append(List[j])
            else:
                result.append(List[j])

        if result[1]:
            flag = result[1]
        else:
            result[1] = flag
        # print(result)
        # ['', 'BELAWAN', '周四', '边行船司', '260', '暂不接', '暂不接', '20/40', '190718', '中转13天/PKG转（二程船1天航程）']
        message = ["SHANGHAI", result[1], line[0], result[2], result[3], result[4], result[5], result[6], result[7],
                   result[8], result[9]]



if __name__ == "__main__":
    Cookie = get_cookie()
    data = get_data(Cookie)
    for i in range(0, 12):
        target = "lnkHx" + str(i)
        data["__EVENTTARGET"] = target
        get_messages(Cookie, data=data)