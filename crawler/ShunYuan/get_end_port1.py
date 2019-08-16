import requests
import json

def get_end_port(startPortCode):
    url = "http://www.51safround.com/page-web/search_all_dest_port.html"

    payload = {'start_port_code':startPortCode}
    headers = {
        'Cookie': "JSESSIONID=2F8AFB58CBCCD77B4D95C8A518A4D6C5; name=1; chatsize=0; UM_distinctid=16c3d128203468-07cb5cd4700f21-3a65420e-144000-16c3d12820433b; growth=; offline=; WC_UID=9481; WC_JUID=9481-a3412a04edfe4376bbd1313ea1d4cdbc; USER_NAME=19979648720; USER_TYPE=0; COMCODE=8800; COMCODE_STATUS=0; NICK_NAME=loyal; ENABLE_PRICE=1; logined=false; indexSearch=; CNZZDATA1273593192=1237074893-1564390852-https%253A%252F%252Fwww.baidu.com%252F%7C1564548859; Hm_lvt_6915824c43dd7788f9885b736a05d5a1=1564450362,1564477124,1564477153,1564553364; JSESSIONID=5857D35D554635753C2B073F46AB8751; twoHoursLaterAppear=true; Hm_lpvt_6915824c43dd7788f9885b736a05d5a1=1564553369",
        'Host': "www.51safround.com",
        'Origin': "http://www.51safround.com",
        'Proxy-Connection': "keep-alive",
        'Referer': "http://www.51safround.com/page-web/search.html?num=3",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url,data=payload,headers=headers)
        res = json.loads(response.text)
        destPortList = res.get('destPortList')

        start2end = {}
        end_port = []
        for destPort in destPortList:
            end_port_data = {}
            end_port_data['port_code'] = destPort.get('port_code')
            end_port_data['port_name'] = destPort.get('port_name')
            end_port_data['port_cname'] = destPort.get('port_cname')
            end_port_data['start_port_code'] = destPort.get('start_port_code')
            end_port.append(end_port_data)
        print(f'{startPortCode}数据存储成功')
        start2end[startPortCode] = end_port
        return start2end
    except:
        print("error")

if __name__ == "__main__":
    with open('all_start_port.json','r',encoding='utf8') as f:
        string = f.read()
    startports = json.loads(string)

    data = {}
    for startport in startports:
        startPortCode = startport.get('port_code')
        start2end = get_end_port(startPortCode)
        data.update(start2end)

    with open("all_end_port.json", 'w', encoding='utf8') as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))