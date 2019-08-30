import requests
import re
import json

data = {"1":"新西兰",
        "2":"澳洲线",
        "3":"地中海",
        "4":"东南亚",
        "5":"非洲线",
        "6":"国线",
        "7":"红海线",
        "8":"加拿大线",
        "9":"美国线",
        "10":"欧洲线",
        "12":"台湾线",
        "13":"香港线",
        "14":"印巴线",
        "15":"中东线",
        "16":"中国线",
        "17":"中南美",
        "11":"日本",
        "18":"日本"
}


url = "http://www.cn956.com/public/autocomplete/data.gzjs"

querystring = {"verson":"2.2"}

headers = {
    'Referer': "http://www.cn956.com/club9/fclfreight.shtml?stport=CNSHA&stportnm=SHANGHAI&enport=6199746&enportnm=NHAVA%20SHEVA&gp20num=1",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "a556d0d6-a22c-4526-ac08-83fb8184aee4,b907ec19-78b9-48d5-9dc6-2522cd615617",
    'Host': "www.cn956.com",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

line_data = {}
messages = re.findall(r"endports\[\d+\] = new Array(.*);", response.text)

for message in messages:
    li_str = re.search(r"\'(.*)\'", message).group()
    li_list = li_str.split("\',\'")
    for i in range(len(li_list)):
        li_list[i] = li_list[i].replace('\'', '')
    print(li_list)
    line_data.update({li_list[2]: data.get(li_list[0])})


with open('endport_route.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(line_data, indent=2, ensure_ascii=False))