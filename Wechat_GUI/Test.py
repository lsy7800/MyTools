import sys
from WeChat_GUI import Ui_MainWindow
from PyQt5.QtWidgets import *
from WeChat_Thread import *
from WeChat_login import *

class My_Mainwindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(My_Mainwindow,self).__init__()
        self.setupUi(self)
        self.single_func()
        self.time = self.dateEdit.text()

    def single_func(self):
        # 点击读取时间
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.getCookies)

    def getCookies(self):
        self.thread2 = LoginThread()
        self.thread2.start()
        self.thread2.sinlogin.connect(self.display)

    def start(self):
        self.display('您选取的时间节点为:{}'.format(self.time))
        self.thread = NewThread(self.time)
        self.thread.sinOut.connect(self.display)
        self.thread.sinOut2.connect(self.showprocess)
        self.thread.sinOut3.connect(self.showtime)
        self.thread.start()
        print('线程开启')
        self.pushButton.setEnabled(False)

    def display(self,msg):
        self.textBrowser.append(msg)

    def showprocess(self,value):
        self.progressBar.setValue(value)

    def showtime(self,num):
        self.lcdNumber.display(num)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = My_Mainwindow()
    mywin.show()
    sys.exit(app.exec_())