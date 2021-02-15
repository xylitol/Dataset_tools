import sys
import os
import shutil
import cv2

DIR_1 = "front"
DIR_2 = "side"
DIR_3 = "back"
DIR_4 = "delete"

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def findPic(picname, sel_path):
    for path,dirs,files in os.walk(sel_path):
        if picname in files:
            return path
    print("\n" + picname + " 이미지를 찾을 수 없습니다")
    exit()

def main():
    path = os.path.dirname(os.path.abspath(__file__)) #실행파일 위치 받아오기
    print("path " + path)
    directories = os.listdir(path) #하위 디렉토리 리스트
    directories.remove(os.path.basename(__file__))
    tmp_idx = None

    i = 1
    for directory in directories:
        print(str(i) + ". " + directory)
        i += 1

    index = int(input("폴더를 선택하세요 : "))
    index -= 1
    sel_path = path + "\\" + directories[index]

    os.chdir(sel_path)
    dir1 = sel_path + "\\" + DIR_1
    dir2 = sel_path + "\\" + DIR_2
    dir3 = sel_path + "\\" + DIR_3
    dir4 = sel_path + "\\" + DIR_4

    createFolder(dir1)
    createFolder(dir2)
    createFolder(dir3)
    createFolder(dir4)

    images = os.listdir(sel_path) #선택한 경로의 하위 디렉토리 목록에서 각 폴더명은 삭제
    images.remove(DIR_1)
    images.remove(DIR_2)
    images.remove(DIR_3)
    images.remove(DIR_4)

    index = 0
    while True:
        if index == len(images):
            break
            
        if os.path.isfile(sel_path + "\\" + images[index]):
            image_path = sel_path + "\\" + images[index]
            os.chdir(sel_path)
        else:
            image_path = findPic(images[index], sel_path)
            os.chdir(image_path)
            image_path = os.path.join(image_path, images[index])
        
        image = cv2.imread("./" + images[index])
        image = cv2.resize(image, (1000, 720))

        
        while True:
            print(images[index], end=" ", flush=True)
            cv2.imshow("image", image)
            key = cv2.waitKey(0)

            try:
                if key == ord('a'):#dir1로 이동
                    print(DIR_1)
                    shutil.move(image_path, dir1)

                elif key == ord('s'):#dir2로 이동
                    print(DIR_2)
                    shutil.move(image_path, dir2)

                elif key == ord('d'):#dir3로 이동
                    print(DIR_3)
                    shutil.move(image_path, dir3)

                elif key == 32:#dir4로 이동
                    print(DIR_4)
                    shutil.move(image_path, dir4)

                elif key == ord('b'):#이전 사진, 이미지 읽어올때 index값, 이전 계속할 때
                    if index <= 0:
                        print("이전 사진이 없습니다")
                        continue
                    if tmp_idx == None:
                        tmp_idx = index
                    index -= 1
                    image_path = findPic(images[index], sel_path)
                    os.chdir(image_path)
                    image_path = os.path.join(image_path, images[index])
                    image = cv2.imread("./" + images[index])
                    image = cv2.resize(image, (1000, 720))
                    print("이전사진으로")
                    continue
                
                
                elif key == ord('q'):#종료
                    print("-----")
                    print("종료")
                    exit()

                else:
                    print("키를 잘못 눌렀습니다(a: dir1, s: dir2, d: dir3, spacebar: dir4, q:quit)")
                    continue

            except shutil.Error:
                pass

            break 

        index += 1
    print("더이상 분류할 사진이 없습니다")
            
        


if __name__ == "__main__":
    main()