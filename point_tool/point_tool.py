#python .\tool+window.py --path '.\test'
#사진 확대 기능

import sys
import subprocess
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QSlider, QLCDNumber, QVBoxLayout, QMainWindow, QColorDialog, QCheckBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5 import uic

# pip가 없으면 pip를 설치한다.
try:
    import pip
except ImportError:
    print("Install pip for python3")
    subprocess.call(['sudo', 'apt-get', 'install', 'python3-pip'])

# cv가 없으면 cv를 설치한다.
try:
    import cv2
except ModuleNotFoundError:
    print("Install opencv in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'opencv-python'])
finally:
    import cv2

# argparse가 없으면 argparse를 설치한다.
try:
    import argparse
except ModuleNotFoundError:
    print("Install argparse in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'argparse'])
finally:
    import argparse

# numpy가 없으면 numpy를 설치한다.
try:
    import numpy
except ModuleNotFoundError:
    print("Install numpy in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'numpy'])
finally:
    import numpy as np

num_hor_points = 13
dir_del = None
clicked_points = []
del_idx = None
index_points = []
index_hor = 0
index_ver = 0
selected_points = []
selected_flag = 0
clone = None
pointColor = [155, 188, 54]
draw_idx = False
form_class = uic.loadUiType("untitled.ui")[0]

class MyApp(QMainWindow, form_class):
    pcolor = [155, 188, 54]
    idir = 0
    check = False
    def __init__(self):
        super().__init__()
        self.setupUi(self) #designer로 만든 UI로 설정
        self.setWindowTitle('Point tool') #창 제목
        self.colorButton.setStyleSheet('background-color: rgb(54, 188, 155)') #색 지정 버튼 색
        self.colorButton.clicked.connect(self.showColorDlg) #색 지정 버튼 눌렀을 때
        self.checkBox.stateChanged.connect(self.checkBox_select) #체크박스 상태 바뀌었을 때
        self.appBtn.clicked.connect(self.apply) #apply 버튼 클릭시
        self.center() #창 화면 중앙 정렬

    def center(self):
        #화면 중앙값 계산해서 창 위치 조정
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showColorDlg(self):       
        # 색상 대화상자 생성
        color = QColorDialog.getColor()
        MyApp.pcolor.clear()
        MyApp.pcolor.append(color.blue())
        MyApp.pcolor.append(color.green())
        MyApp.pcolor.append(color.red())
        self.colorButton.setStyleSheet('background-color: {}'.format( color.name()))

    def checkBox_select(self):
        if self.checkBox.isChecked():
            MyApp.check = True
        else:
            MyApp.check = False

    def apply(self):
        global pointColor, draw_idx, num_hor_points
        pointColor = MyApp.pcolor[:]
        draw_idx = MyApp.check
        num_hor_points = int(self.lineEdit.text())
        Draw_Point()

app = QApplication(sys.argv)
ex = MyApp()
ex.show()


def GetArgument():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Enter the image files path")
    ap.add_argument("--sampling", default=1, help="Enter the sampling number.(default = 1)")
    args = vars(ap.parse_args())
    path = args['path']
    sampling = int(args['sampling'])
    return path, sampling

def MouseClick(event, x, y, flags, param):
    global index_hor, index_ver, selected_flag, selected_points, del_idx, clicked_points, pointColor

    if event == cv2.EVENT_RBUTTONDOWN:#우클릭시 좌표 선택
        for i, point in enumerate(clicked_points):#일정 범위 내의 좌표를 찾아 선택
            if((y - 5) <= point[0] <= (y + 5) and (x - 5) <= point[1] <= (x + 5)):
                ex.textBrowser.append("Select " + str(index_points[i]))
                print("Select" + str(index_points[i]))
                if selected_flag == 1:
                    #선택된 좌표 있으면 좌표 초기화하고 새로운 좌표를 넣어준다
                    selected_points = []
                selected_flag = 1
                selected_points.append(point[0])
                selected_points.append(point[1])
                break

    if event == cv2.EVENT_LBUTTONDOWN:#좌클릭시 새로운 좌표 생성
        if(del_idx != None):#삭제한 좌표가 있으면 그 인덱스에 좌표 생성
            print(del_idx, (y,x))
            clicked_points.insert(del_idx, (y,x))
            ex.textBrowser.append(str(index_points[del_idx]))
            del_idx = None
        else:
            clicked_points.append((y, x))
            index_points.append((index_hor,index_ver))
            print(index_hor, index_ver)
            ex.textBrowser.append("(" + str(index_hor) + "," + str(index_ver) + ")")
        


        if index_ver == num_hor_points :#인덱스 바꿔주는 부분
            index_hor += 1
            index_ver = 0
            ex.textBrowser.append("Next Line")
        else : 
            index_ver += 1
        
    # 원본 파일을 가져 와서 clicked_points에 있는 점들을 그린다.
    Draw_Point()

def Del_Point():#선택된 좌표, 직전 좌표 구분하여 삭제
    global clicked_points, index_points, index_hor, index_ver, selected_points, selected_flag, del_idx
    if len(clicked_points) > 0:
        if(selected_flag == 0):#선택된 점 존재 유무 판별
            #선택된 점 없으면 직전 좌표 삭제
            ex.textBrowser.append("Delete " + str(index_points[-1]))
            clicked_points.pop()
            index_points.pop()
        else:
            #선택된 점 있으면 선택된 점의 좌표 저장 후 삭제
            del_idx = clicked_points.index((selected_points[0], selected_points[1]))
            clicked_points.remove((selected_points[0], selected_points[1]))
            ex.textBrowser.append("Delete " + str(index_points[del_idx]))
            print(index_points[del_idx])
            selected_points = []#선택된 점 좌표, flag 변수 초기화
            selected_flag = 0

        if(index_ver == 0 and index_hor > 0):
            index_hor -= 1
            index_ver = num_hor_points
        elif(index_ver == 0 and index_hor == 0):
            pass
        else:
            index_ver -= 1
    else:
        ex.textBrowser.append("no more points")

def Draw_Point():
    global clone, clicked_points, selected_flag, selected_points, pointColor, index_points
    img = clone.copy()

    for point, index in zip(clicked_points, index_points):
        cv2.circle(img, (point[1], point[0]), 2, pointColor, thickness = -1)
        if draw_idx == True:
            cv2.putText(img, str(index[0]) + "," + str(index[1]), org=(point[1] - 10, point[0] - 5), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 255, 255), thickness=1)
    if(selected_flag == 1):
        cv2.circle(img, (selected_points[1], selected_points[0]), 4, (0, 255, 255), thickness = -1)
    cv2.imshow("image", img)


def main():
    global clone, clicked_points, index_points, index_hor, index_ver, pointColor
    
    # 이미지 디렉토리 경로를 입력 받는다.
    path, sampling = GetArgument()
    # path의 이미지명을 받는다.
    image_names = os.listdir(path)

    print("1. 입력한 파라미터인 이미지 경로(--path)에서 이미지들을 차례대로 읽어옵니다")
    print("2. 찍었던 좌표를 우클릭하면 해당 좌표를 선택할 수 있습니다")
    print("3. 키보드에서 'n'을 누르면 다음 이미지로 넘어갑니다. 이 때, 작업한 점의 좌표가 저장 됩니다")
    print("4. 키보드에서 'l'를 누르면 다음 줄로 건너뜁니다")
    print("5. 키보드에서 'p'를 누르면 다음 점 인덱스로 건너뜁니다")
    print("6. 키보드에서 'b'를 누르면 직전에 입력한 좌표 혹은 선택된 좌표를 취소한다")
    print("7. 키보드에서 'q'를 누르면 프로그램이 종료됩니다.(n 안누른 사진은 저장 안됩니다)")
    print("----------\n출력 포맷 : \n이미지명\ny1,x1\ny2,x2\n...\n----------")

    # path를 구분하는 delimiter를 구한다.
    if len(path.split('\\')) > 1:
        dir_del = '\\'
    else :
        dir_del = '/'

    # path에 입력된 마지막 폴더 명을 구한다.    
    folder_name = path.split(dir_del)[-1]

    # 결과 파일을 저장하기 위하여 현재 시각을 입력 받는다.
    now = datetime.now()
    now_str = "%s%02d%02d_%02d%02d%02d" % (now.year - 2000, now.month, now.day, now.hour, now.minute, now.second)  
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", MouseClick)

    for idx, image_name in enumerate(image_names):
        if (idx % sampling != 0):
            continue

        image_path = path + dir_del + image_name
        image = cv2.imread(image_path)
        flag = False

        while True:
            clone = image.copy()
            Draw_Point()
            key = cv2.waitKey(0)

            if key == ord('n'):
                # 텍스트 파일을 출력 하기 위한 stream을 open 합니다.
                # 중간에 프로그램이 꺼졌을 경우 작업한 것을 저장하기 위해 쓸 때 마다 파일을 연다.
                file_write = open('./' + now_str + '_' + folder_name + '.txt', 'a+')

                text_output = image_name
                text_output += '\n'
                for point, index in zip(clicked_points, index_points):
                    text_output += str(index[0]) + "," + str(index[1])
                    text_output += '\n'
                    text_output += str(point[0]) + "," + str(point[1])
                    text_output += '\n'
                text_output += '\n'
                file_write.write(text_output)
                
                # 클릭한 점, 인덱스 초기화
                clicked_points = []
                index_points = []
                index_hor = 0
                index_ver = 0

                # 파일 쓰기를 종료한다.
                file_write.close()
                break

            if key == ord('d'):
                Del_Point()
            
            if key == ord('l'):
                index_hor += 1
                index_ver = 0
                ex.textBrowser.append("Skip Line")

            if key == ord('p'):
                index_ver += 1
                ex.textBrowser.append("Skip point")

            if key == ord('q'):
                # 프로그램 종료
                flag = True
                break

        if flag:
            break

    # 모든 window를 종료합니다.
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()
