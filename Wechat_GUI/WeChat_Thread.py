from PyQt5.QtCore import QThread, pyqtSignal
import time, os, re, requests, json, random, csv

class NewThread(QThread):
    sinOut = pyqtSignal(str)
    sinOut2 = pyqtSignal(float)
    sinOut3 = pyqtSignal(int)

    def __init__(self, date):
        super(NewThread, self).__init__()
        self.date = date
        self.gz_dict = self.make_dict()
        self.sumnum = len(self.gz_dict)
        print(self.sumnum)

    def getDate(self, times):
        '''毫秒数转换为日期'''
        time_arr = time.localtime(times)
        date = time.strftime("%Y-%m-%d %H:%M:%S", time_arr)
        return date

    def getDate2(self, times):
        '''时间转毫秒'''
        t1 = time.strptime(times, "%Y-%m-%d")
        # print(t1)
        date2 = int(time.mktime(t1)) * 1000
        return date2

    def getDate3(self, times):
        '''时间转毫秒'''
        t1 = time.strptime(times, "%Y/%m/%d")
        # print(t1)
        date3 = int(time.mktime(t1)) * 1000
        return date3

    def make_dict(self):
        school_list = {}
        with open('school_account.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for line in reader:
                school_name = {line[0]: line[1]}
                school_list.update(school_name)
        return school_list

    def listAllArticle(self, account_name, query):
        # 目标url
        url = "https://mp.weixin.qq.com"

        # header信息
        headers = {
            "HOST": "mp.weixin.qq.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        }

        # 读取已经保存至本地的cookie
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read()
        cookies = json.loads(cookie)
        self.sinOut.emit('cookies 已读取成功！')

        # 使用正则匹配获取Token
        response = requests.get(url=url, cookies=cookies, headers=headers)
        token = re.findall(r"(\d+)", str(response.url))[0]
        # print('token:{}'.format(token))

        # 搜索微信公众号的接口地址
        search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

        query_id = {
            'action': 'search_biz',
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'query': query,
            'begin': '0',
            'count': '5'
        }

        # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
        search_response = requests.get(search_url, cookies=cookies, headers=headers, params=query_id)
        # 取搜索结果中的第一个公众号
        lists = search_response.json().get('list')[0]
        # 获取这个公众号的Fake_id，后面爬取公众号文章需要此字段
        fakeid = lists.get('fakeid')
        # print(fakeid)

        # 微信公众号文章接口地址
        appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
        # 搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '0',  # 不同页，此参数变化，变化规则为每页加5
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
        }

        # 打开搜索的微信公众号文章列表页
        appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=headers, params=query_id_data).json()

        # 创建文件夹
        date_now = time.strftime("%Y-%m-%d")
        path = '{}'.format(date_now)
        if not os.path.exists(path):
            os.mkdir(path)

        # 开始下载文件
        with open(path + '\\' + date_now + '.csv', 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for item in appmsg_response['app_msg_list']:

                # 避免频率过快加入随机睡眠
                time.sleep(random.randint(1, 5))
                # 提取每页文章的标题及对应的url
                items = ['{}'.format(account_name), item["title"], item["link"], item["cover"],
                         self.getDate(item["create_time"]), item["digest"],
                         self.getDate(item["update_time"]), ''.join(fakeid)]

                jud1 = items[4].split(' ')[0]
                jud1 = self.getDate2(jud1)
                jud2 = self.getDate3(self.date) #如何获取前端的时间
                if jud1 >= jud2:
                    self.sinOut.emit('文章:{}符合当前时间节点需求'.format(items[1]))
                    writer.writerow(items)
                else:
                    self.sinOut.emit('文章:{}不符合当前时间节点要求'.format(items[1]))

    def run(self):
        count = 0
        n = 0
        for k,v in self.gz_dict.items():
            start = time.time()
            self.sinOut.emit('开始获取公众号{}'.format(k))
            self.listAllArticle(account_name=k, query=v)
            self.sinOut.emit('写入完成')

            count +=1
            process = round(count/self.sumnum,2)*100
            print(process)
            if count == 31:
                self.sinOut2.emit(100)
            else:
                self.sinOut2.emit(process)
            end = time.time()
            t3 = round((end-start),0)
            n += t3
            time.sleep(1)
            self.sinOut3.emit(n)


        self.sinOut.emit('信息获取已完成！')