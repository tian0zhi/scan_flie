from main_ui import Ui_MainWindow
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QProgressBar   #导入PyQt相关模块
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import threading
import os
import re

def get_file_path(root_path,file_list,dir_list):
    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path+'/',dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            #递归获取所有文件和目录的路径
            get_file_path(dir_file_path,file_list,dir_list)
        else:
            file_list.append(dir_file_path)

def get_file_path_nore(root_path,file_list,dir_list):
    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path+'/',dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
        else:
            file_list.append(dir_file_path)

class MyWindow(QMainWindow, Ui_MainWindow):
    senmsg = pyqtSignal(str)
    senmsg_for_files_show = pyqtSignal(str)
    sendint_for_pb = pyqtSignal(int)
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('文件过滤生成器')
        self.setWindowIcon(QIcon("fa.png"))
        self.folder_path = ''
        self.all_files = []
        self.filter_files = []
        self.QWt = QWidget()
        self.QWt.setWindowTitle("写入中")
        self.QWt.setWindowIcon(QIcon("fa.png"))
        self.QWt.resize(300, 40)
        self.pgb = QProgressBar(self.QWt)
        self.pgb.move(25, 10)
        self.pgb.resize(250, 20)
        self.pgb.setStyleSheet(
            "QProgressBar { border: 2px solid grey; border-radius: 5px; color: rgb(20,20,20);  background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background-color: rgb(100,200,200); border-radius: 10px; margin: 0.1px;  width: 1px;}")
        ## 其中 width 是设置进度条每一步的宽度
        ## margin 设置两步之间的间隔
        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setWeight(30)
        self.pgb.setFont(font)
        # 设置进度条的范围
        self.pgb.setMinimum(0)
        self.pgb.setMaximum(100)
        self.pgb.setValue(0)
        self.senmsg.connect(self.showMessage)
        self.senmsg_for_files_show.connect(self.show_file_Message)
        self.sendint_for_pb.connect(self.ProgressBarcontrol)
        self.open_folder_Button.clicked.connect(self.select_dir)
        self.filter_pushButton.clicked.connect(self.filter)
        self.pushButton.clicked.connect(self.save_file)

    def showMessage(self, info):
        self.output_info_textBrowser.append(info)

    def show_file_Message(self, info):
        self.file_list_textBrowser.append(info)

    def select_dir(self):
        """选择文件夹对话框架"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择文件夹', os.getcwd())
        if dir_path:
            self.senmsg.emit("选择文件夹成功：{}".format(dir_path))
            self.folder_path_lineEdit.clear()
            self.folder_path_lineEdit.setText(dir_path)
            self.folder_path = dir_path

    def save_file(self):
        if len(self.filter_files)<1:
            self.senmsg.emit("未过滤筛选文件或无符合条件的文件")
            return
        name = QFileDialog.getSaveFileName(self, 'Save File', "File_list.txt")
        print(name)
        if len(name[0])>1:
            self.pgb.setValue(0)
            self.QWt.show()
            thread = threading.Thread(target=self.save_file_thread,args=(name[0],), daemon=False)
            thread.start()

    def save_file_thread(self,file_path):
        file_num = len(self.filter_files)
        count = 0
        with open(file_path,'w') as f:
            for line in self.filter_files:
                f.write(line+'\n')
                count = count + 1
                self.sendint_for_pb.emit(int(count/file_num)*100)
        if count == 0:
            self.sendint_for_pb.emit(100)
    def ProgressBarcontrol(self,value):
        if value != 100:
            self.pgb.setValue(value)
        else:
            self.pgb.setValue(value)
            self.QWt.close()
    def filter(self):
        if len(self.folder_path) < 1:
            self.senmsg.emit("未选择文件夹路径")
            return
        self.senmsg.emit("清除文件列表!")
        self.file_list_textBrowser.clear()
        thread = threading.Thread(target=self.filter_thread, daemon = False)
        thread.start()
        print("over")

    def filter_thread(self):
        # file_names = os.listdir(self.folder_path)
        file_names = []
        folder_names = []
        self.filter_files = []
        self.senmsg.emit("#######################")
        self.senmsg.emit("后缀名(&)： "+self.rear_name_lineEdit.text())
        self.senmsg.emit("包含字符s： "+self.contain_char_lineEdit.text())
        self.senmsg.emit("正则表达式：" + self.zhengze_lineEdit.text())
        self.senmsg.emit("#######################")
        self.senmsg.emit("符合条件的文件获取中....")
        if self.checkBox.checkState():
            self.senmsg.emit("递归遍历")
            get_file_path(self.folder_path,file_names,folder_names)
        else:
            self.senmsg.emit("非递归遍历")
            get_file_path_nore(self.folder_path,file_names,folder_names)
            #file_names = os.listdir(self.folder_path)
        for elem in file_names:
            # if os.path.isdir(os.path.join(self.folder_path+'/',elem)):
            #     continue
            full_elem = elem
            elem = elem.split('/')[-1]
            if len(self.rear_name_lineEdit.text()) > 0:
                rear_list = self.rear_name_lineEdit.text().split('&')
                if not elem.endswith(tuple(rear_list)):
                    continue
            if len(self.contain_char_lineEdit.text()) > 0:
                if self.contain_char_lineEdit.text() not in elem:
                    continue
            if len(self.zhengze_lineEdit.text()) > 0:
                if re.search(self.zhengze_lineEdit.text(), elem, flags = 2):
                    pass
                else:
                    continue
            self.filter_files.append(full_elem)
            self.senmsg_for_files_show.emit(elem)
        self.senmsg.emit("符合条件的文件列表获取完毕!\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()  # 创建对象
    myWin.show()  # 显示窗口
    sys.exit(app.exec_())  # `的对象，启动即可。