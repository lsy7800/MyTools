import requests,random,time,csv,json,re,os
from selenium import webdriver


def getDate(times):
    '''毫秒数转换为日期'''
    time_arr = time.localtime(times)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time_arr)
    return date

def getDate2(times2):
    '''时间转毫秒'''
    t1 = time.strptime(times2, "%Y-%m-%d")
    # print(t1)
    date2 = int(time.mktime(t1)) * 1000
    return date2


def weChat_login():
    '''由于公众号的Fake_id和Token每天都在变化，所以每次都需要重新获取信息'''

    # 定义一个空字典存放cookie
    post = {}

    # 使用驱动启动谷歌浏览器
    print("正在启动Google浏览器，打开微信公众号登录界面")
    print("==========" * 20)
    print("如果不能正常启动，请检查Chromedriver版本是否过期")
    print("1.点击谷歌浏览器右上方的'...'->'帮助'->'关于Google Chrome'")
    print("2.检查谷歌浏览器版本号")
    print("3.登录'https://chromedriver.chromium.org/downloads'下载对应版本驱动至对应文件夹")
    print("4.如仍旧不能正常启动，请联系工程师")
    print("==========" * 20)

    driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")

    # 打开微信公众号登录页面
    driver.get('https://mp.weixin.qq.com/')
    # 扫描二维码！
    print("请使用手机扫描二维码登录公众号")
    time.sleep(15)
    print("登录成功")

    # 重新载入公众号登录页，登录之后会显示公众号后台首页，从这个返回内容中获取cookies信息
    driver.get('https://mp.weixin.qq.com/')
    # 获取cookies
    cookie_items = driver.get_cookies()
    # 获取到的cookies是列表形式，将cookies转成json形式并存入本地名为cookie的文本中
    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post)
    with open('cookie.txt', 'w+') as f:
        f.write(cookie_str)
    print("cookies信息已保存到本地")

    # 关闭浏览器
    driver.close()

def listAllArticle(account_name,query):
    '''获取微信文章列表以及信息'''

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

    # 使用正则匹配获取Token
    response = requests.get(url=url, cookies=cookies)
    token = re.findall(r"(\d+)", str(response.url))[0]

    # 搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

    query_id = {
        'action': 'search_biz',
        'token' : token,
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
    print(lists)
    # 获取这个公众号的Fake_id，后面爬取公众号文章需要此字段
    fakeid = lists.get('fakeid')

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

    #打开搜索的微信公众号文章列表页
    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=headers, params=query_id_data).json()

    # 创建文件夹
    date_now = time.strftime("%Y-%m-%d")
    path = '{}'.format(date_now)
    if not os.path.exists(path):
        os.mkdir(path)

    # 开始下载文件
    with open(path+'\\'+date_now+'.csv', 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for item in appmsg_response['app_msg_list']:

            # 避免频率过快加入随机睡眠
            time.sleep(random.randint(1,5))
            # 提取每页文章的标题及对应的url
            items = ['{}'.format(account_name),item["title"], item["link"], item["cover"], getDate(item["create_time"]), item["digest"],
                     getDate(item["update_time"]), ''.join(fakeid)]

            jud1 = items[4].split(' ')[0]
            jud1 = getDate2(jud1)
            jud2 = getDate2(date)
            if jud1 >= jud2:
                print(items)
                writer.writerow(items)
            else:
                print('{}不符合当前时间节点要求'.format(items[0]))

def make_dict():
    school_list = {}
    with open('school_account.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for line in reader:
            school_name = {line[0]: line[1]}
            school_list.update(school_name)
    return school_list

if __name__ == '__main__':

    # 暂无信息学校
    # '天津益中西青学校': 'gh_e60f17c3e6d1'，'天津市实验中学': 'gh_a972ac8d7d37','天津市河西区天津学校': 'tjxx2006'

    # gz_dict={'天津市第一中学': 'tianjinyizhong', '天津市耀华中学': 'yaohua1927', '天津市第二十中学': 'tj20ms',
    #          '天津市第二南开中学': 'tj2nankai', '天津市第五十五中学': 'tj55zhongxue','天津市双菱中学': 'gh_9ab3f45b3ea8',
    #          '天津市耀华嘉诚国际中学': 'tjsyhjcgjzx', '天津市建华中学': 'tjjhzx','天津市新华中学': 'tjsxhzx',
    #          '天津市第四十二中学': 'tj42zx','天津市第四十一中学': 'tj41zhong', '天津市第四中学': 'tjsztjzl',
    #          '天津市海河中学': 'hhzx1895','北京师范大学天津附属中学': 'BSDTJFZ', '天津市第二新华中学': 'gh_cebafcff8505',
    #          '天津市梧桐中学': 'gh_87f940c8f68b','天津市南开中学': 'tjsnkzx', '天津市天津中学': 'Tianjin_school',
    #          '南开大学附属中学': 'nkdxfszx','天津大学附属中学': 'tjdxfszx', '天津市第七中学': 'gh_197fbeeba16e',
    #          '天津市第二中学': 'tjerzhong','天津市第三中学': 'tj3zhong', '天津市翔宇国际学校': 'gh_4ba7b140651a',
    #          '天津市新华圣功学校': 'gh_3acbbb0b5666','天津市河西区实验求是学校': 'gh_220ffd4f8057',
    #          '天津市河西区汇德学校': 'gh_ff09d28a169e','天津市逸阳梅江湾国际学校': 'yymjw2007',
    #          '天津外国语大学附属外国语学校': 'gh_5cd1256751cc','天津英华国际学校': 'yinghuaguojixuexiao',
    #          '六力国际学校': 'tianjinliulixuexiao', '天津为明国际学校': 'TJWMEDU'}
    gz_dict = make_dict()


    try:
        # 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
        # 登录之后，通过微信公众号后台提供的微信公众号文章接口爬取文章
        weChat_login()

        # 输入需要抓取的时间节点
        date = input('请输入您要抓取的时间节点，(例如：2021-05-17):')

        # 开始循环抓取链接
        for account_name,query in gz_dict.items():
            #爬取微信公众号文章，并存在本地文本中
            print("开始爬取公众号：" + account_name)
            listAllArticle(account_name=account_name,query=query)
            print("爬取完成")

    except Exception as e:
        print(str(e))
