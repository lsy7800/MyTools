from PyQt5.QtCore import QThread, pyqtSignal
from selenium import webdriver
import time, json

class LoginThread(QThread):
    sinlogin = pyqtSignal(str)
    def __init__(self):
        super(LoginThread, self).__init__()

    def run(self):
        post = {}
        option = webdriver.ChromeOptions()
        # 防止打印一些无用的日志
        option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        driver = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",chrome_options=option)
        # 打开微信公众号登录页面
        driver.get('https://mp.weixin.qq.com/')
        # 扫描二维码！
        self.sinlogin.emit('请扫描二维码登陆')
        time.sleep(15)
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
        self.sinlogin.emit('cookies信息已保存至本地')