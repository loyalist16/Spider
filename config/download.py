# -*- coding:utf-8 -*-
import requests
import time
import random
import logging

# 使用阿布云代理ip
class Abuyun():
    def __init__(self):
        # user-agents池
        self.user_agents = [
            # Opera
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Opera/8.0 (Windows NT 5.1; U; en)",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
            # Firefox
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            # Safari
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            # chrome
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            # 360
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            # 淘宝浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            # 猎豹浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            # QQ浏览器
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            # sogou浏览器
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
            # maxthon浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
            # UC浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        ]
        self.logger = logging.getLogger('main.abuyun')

    def get(self, url, headers, num_retry=5, params=None):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent":UA}
        headers_ua.update(headers) ## 完整的 headers
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        # 代理隧道验证信息
        proxyUser = "H71875T07R5145PD"
        proxyPass = "1FB5BCB5011EC232"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        try:
            self.logger.debug(f"当前使用代理：{proxies}")
            response = requests.get(url, headers=headers_ua, timeout=5, proxies=proxies, params=params)
            if response.status_code != 200:
                return self.get(url, headers, num_retry-1, params=params)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(3)
                return self.get(url, headers, num_retry-1, params=params)
            else:
                self.logger.error('代理无效,将使用本地IP')
                return requests.get(url, headers=headers_ua, proxies=None, timeout=5 )

    def post(self, url, headers, data,num_retry=5):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent": UA}
        headers_ua.update(headers)  ## 完整的 headers
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        # 代理隧道验证信息
        proxyUser = "H71875T07R5145PD"
        proxyPass = "1FB5BCB5011EC232"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        try:
            self.logger.debug(f"当前使用代理：{proxies}")
            response = requests.post(url, headers=headers_ua, data=data,timeout=5, proxies=proxies)
            if response.status_code != 200:
                return self.post(url, data, headers, num_retry)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(3)
                return self.post(url, data, headers, num_retry-1)
            else:
                self.logger.error('代理无效,将使用本地IP')
                return requests.post(url, headers=headers_ua, timeout=5, data=data)

# 不使用代理ip
class NoProxy():
    def __init__(self):
        # user-agents池
        self.user_agents = [
            # Opera
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Opera/8.0 (Windows NT 5.1; U; en)",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
            # Firefox
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            # Safari
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            # chrome
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            # 360
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            # 淘宝浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            # 猎豹浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            # QQ浏览器
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            # sogou浏览器
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
            # maxthon浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
            # UC浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        ]
        self.logger = logging.getLogger('main.noproxy')

    def get(self, url, headers, num_retry=5, params=None):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent":UA}
        headers_ua.update(headers) ## 完整的 headers

        try:

            response = requests.get(url, headers=headers_ua, timeout=5, params=params)
            if response.status_code != 200:
                return self.get(url, headers, num_retry - 1, params=params)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(5)
                return self.get(url, headers, num_retry-1, params=params)
            else:
                return requests.get(url, headers=headers_ua, proxies=None, timeout=5)

    def post(self, url, headers, data,num_retry=3):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent": UA}
        headers_ua.update(headers)  ## 完整的 headers

        try:
            response = requests.post(url, headers=headers_ua, data=data, timeout=5)
            if response.status_code != 200:
                return self.post(url, data, headers, num_retry)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(10)
                return self.post(url, data, headers, num_retry-1)
            else:
                return requests.post(url, headers=headers_ua, timeout=5, data=data)

# 使用大神给的代理IP
class Dashenip():
    def __init__(self):
        # user-agents池
        self.user_agents = [
            # Opera
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Opera/8.0 (Windows NT 5.1; U; en)",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
            # Firefox
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            # Safari
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            # chrome
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            # 360
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            # 淘宝浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            # 猎豹浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            # QQ浏览器
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            # sogou浏览器
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
            # maxthon浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
            # UC浏览器
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        ]
        self.usable = [
            '101.27.21.49:61234',
            '202.112.51.51:8082',
            '114.239.248.75:808',
            '211.159.219.225:8118',
            '60.205.159.195:3128',
            '88.99.149.188:31288',
            '101.27.23.96:61234',
            '101.27.23.46:61234',
            '187.53.61.50:80',
            '123.163.166.97:808',
            '114.239.0.71:808',
            '200.137.138.2:80',
            '114.239.145.90:808',
            '117.21.111.224:61234',
            '113.121.241.43:61234',
            '114.239.1.233:808',
        ]
        self.logger = logging.getLogger('main.dashen')

    def get(self, url, headers, num_retry=5, params=None):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent":UA}
        headers_ua.update(headers) ## 完整的 headers
        # 代理服务器
        proxyRes = requests.get("http://proxy.zpfdev.com/get/")
        proxyStr = proxyRes.text
        # proxyStr = random.choice(self.usable)
        proxies = {
            "http": "http://" + proxyStr,
            "https": "https://" + proxyStr,
        }


        try:
            self.logger.debug(f"当前使用代理：{proxies}")
            response = requests.get(url, headers=headers_ua, timeout=5, proxies=proxies, params=params)
            if response.status_code != 200:
                return self.get(url, headers, num_retry, params=params)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(3)
                return self.get(url, headers, num_retry-1, params=params)
            else:
                self.logger.error('代理无效,将使用本地IP')
                return requests.get(url, headers=headers_ua, proxies=None, timeout=5 )

    def post(self, url, headers, data,num_retry=5):
        UA = random.choice(self.user_agents) ## 随机拿取 user-agent
        headers_ua = {"User-Agent": UA}
        headers_ua.update(headers)  ## 完整的 headers
        # 代理服务器
        proxyRes = requests.get("http://proxy.zpfdev.com/get/")
        proxyStr = proxyRes.text
        # proxyStr = random.choice(self.usable)
        proxies = {
            "http": "http://" + proxyStr,
            "https": "https://" + proxyStr,
        }


        try:
            self.logger.debug(f"当前使用代理：{proxies}")
            response = requests.post(url, headers=headers_ua, data=data, timeout=5, proxies=proxies)
            if response.status_code != 200:
                return self.post(url, data, headers, num_retry)
            return response
        except:
            self.logger.warning(f"{url}连接错误，正在尝试重新连接,第{6-num_retry}次连接")
            if num_retry > 0:
                time.sleep(3)
                return self.post(url, data, headers, num_retry-1)
            else:
                self.logger.error('代理无效,将使用本地IP')
                return requests.post(url, headers=headers_ua, timeout=5, data=data)
