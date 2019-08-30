import requests,json
from lxml.html import etree

url = "http://www.shflyingeagle.com/yj/frmYj2.aspx"

headers = {
    'Referer': "http://www.shflyingeagle.com/",
    'Host': "www.shflyingeagle.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    'Upgrade-Insecure-Requests': "1",
    'Cookie': "ASP.NET_SessionId=2zgfxjm3jtqvic55inucli55;ASPSESSIONIDQCQCQQSC=JOGOHCOCFJECHCAGOFEPNOHM",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

# response = requests.request("GET", url, headers=headers)

with open('test.html', 'r', encoding='utf-8') as f:
    response = f.read()

with open('company.json', 'r', encoding='utf8') as f:
    companies = json.loads(f.read())

html = etree.HTML(response)
# a = etree.tostring(html)
# print(a.decode('utf-8'))

# 航线
line = html.xpath('//*[@id="lblTypeName"]/text()')[0] #['东南亚线']

# 内容
results = html.xpath('//*[@id="dgdList"]/tr[@class="Row" or @class="AlternatingRow"]')

#目的港
flag = ''

# for i in range(len(results)):
#     List = results[i].xpath('./td//text()')
#     print("========================================================================================")
#     # print(List)
#     result = []
#     for j in range(len(List)):
#         List[j] = List[j].strip()
#         if j >= 2:
#             if List[j]:
#                 result.append(List[j])
#         else:
#             result.append(List[j])
#
#     if result[1]:
#         flag = result[1]
#     else:
#         result[1] = flag
#     # print(result)
#     #['', 'BELAWAN', '周四', '边行船司', '260', '暂不接', '暂不接', '20/40', '190718', '中转13天/PKG转（二程船1天航程）']
#     message = ["SHANGHAI", result[1], line[0], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9]]
#     print(message)


for result in results:
    # 起始港
    origination = "SHANGHAI"
    # 目的港
    destination = result.xpath('./td[1]/span/text()')
    if destination:
        flag = destination = destination[0].strip()
    else:
        destination = flag

    # 船期
    schedule = result.xpath('./td[2]/span/text()')[0].strip()
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
    remark = result.xpath('./td[10]/span/text()')[0].strip()
    message = [origination, destination, line, company, companyCode, schedule, GP20, GP40, HC40, lss, date, remark]
    print("=================================================================")
    print(message)

