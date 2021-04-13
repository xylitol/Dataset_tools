from PIL import Image
from PIL import ImageChops
from PIL import ImageFile
import cv2
import sys, time, os
import numpy as np
import time
ImageFile.LOAD_TRUNCATED_IMAGES = True #truncated image(깨진 이미지) 에러 안뜨게

SIMILARITY_CRITICAL_VALUE = 0.8

#픽셀- 그레이 X, 필터 X, 회전 X, 사이즈 X, 대칭 X
#해쉬- 그레이 O(93), 필터 X, 회전 X, 사이즈 O(93), 대칭 X

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def max_resolution(img_idx, img_path_list):
    print("3/3: Finding max resolution Image")
    for index, img_list in enumerate(img_idx):
        printProgress(index + 1, len(img_idx), 'Progress:', 'Complete', 1, 50)
        max = 0
        max_img = 0
        for img in img_list:
            try: # 특정 이미지가 안열리는 오류시 opencv로 열었다 저장해서 다시 열어 해결하기 위해(원인 못찾음)
                image = Image.open(img_path_list[img]).convert('RGBA') # convert는 PNG파일도 읽기위해
            except:
                print("error" + img_path_list[img])
                exit()
                tmp_np = np.fromfile(img_path_list[img], np.uint8)# 이미지 제목이 한글이면 안열리는거(cv에서만) 해결하기 위해
                tmp_img = cv2.imdecode(tmp_np, cv2.IMREAD_UNCHANGED)
                extension = os.path.splitext(img_path_list[img])[1]
                result, encoded_img = cv2.imencode(extension, tmp_img)
                if result:
                    with open(i, mode='w+b') as f:
                        encoded_img.tofile(f)
                image = Image.open(img_path_list[img]).convert('RGBA')
            resolution = image.size[0] + image.size[1]
            if resolution > max: # 같은 이미지 중 해상도가 가장 높은걸 찾는다
                max = resolution
                max_img = img
        if max != 0: # 해상도 가장 높은걸 찾았다면 그걸 리스트의 맨 앞으로 옮긴다
            max_idx = img_list.index(max_img)
            tmp = img_list[0]
            img_list[0] = img_list[max_idx]
            img_list[max_idx] = tmp
    print()


def dhash(image, hash_size = 8):
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)


def compare_hash_string_similarity(hash1, hash2):
	hash_list = [int(hash1[i:i+1] == hash2[i:i+1]) for i in range(max(len(hash1), len(hash2)))]

	total_chars = len(hash_list)
	total_matches = sum(hash_list)

	hash_sim = total_matches / total_chars

	return hash_sim


def get_image_hash_similarity(li):
    hash_image = [] # 해시값 저장 변수
    sim_list_list = [] # 유사한 이미지 리스트들의 리스트
    flag = False

    print("1/3: Calculating Image hash")
    for index, i in enumerate(li): # li 내 모든 이미지의 해시값 계산
        printProgress(index + 1, len(li), 'Progress:', 'Complete', 1, 50)

        try: # 특정 이미지 파일 안열리는거 해결하기 위해(max_resolution에서와 같은 문제, except까지)
            image = Image.open(i).convert('RGBA')
        except:
            print("열기 오류 예외처리")
            exit()
            tmp_np = np.fromfile(i, np.uint8)
            tmp_img = cv2.imdecode(tmp_np, cv2.IMREAD_UNCHANGED)
            extension = os.path.splitext(i)[1]
            result, encoded_img = cv2.imencode(extension, tmp_img)
            if result:
                with open(i, mode='w+b') as f:
                    encoded_img.tofile(f)
            image = Image.open(i).convert('RGBA')

        hash_image.append(dhash(image))

    remove_list = []
    print("\n2/3: Calculating Similarity") # 해시값으로 이미지 유사도 비교
    for index, i in enumerate(range(len(hash_image)-1)):
        tmp_sim_list = []
        printProgress(index + 1, len(range(len(hash_image)-1)), 'Progress:', 'Complete', 1, 50)

        for li in sim_list_list: # 현재 기준 이미지(i)가 전에 찾은 유사 이미지 목록에 있다면 건너뛴다
            if i in li:
                flag = True
                break
        if flag == True:
            flag = False
            continue

        for j in range(i+1 ,len(hash_image)): # 기준 이미지의 다음 이미지부터 끝까지 비교
            if j in remove_list: # 앞에서 나온 중복된 이미지는 건너뛴다
                continue
            if compare_hash_string_similarity(hash_image[i], hash_image[j]) > SIMILARITY_CRITICAL_VALUE:
            # 유사도가 임계값 이상이면 같은 이미지로 판별
                tmp_sim_list.append(j) # 한 리스트로 묶음(인덱스값을 저장)
                remove_list.append(j)
                

        if len(tmp_sim_list) > 0: # 찾은 중복 이미지 리스트가 있다면
            tmp_sim_list.append(i) # 기준 이미지 삽입
            sim_list_list.append(tmp_sim_list) # 리스트의 리스트로

    print("")

    return sim_list_list, len(hash_image)



if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) #실행파일 위치 받아오기
    print("path " + path)
    fileList = os.listdir(path) #하위 디렉토리 리스트

    directories = []
    i = 0 #폴더 목록 출력
    for directory in fileList:
        if os.path.isdir(directory):
            i += 1
            directories.append(directory)
            print(str(i) + ". " + directory)

    while True: #폴더 선택
        index = input(f'폴더를 선택하세요: ')
        if not (index.isdigit() and int(index) in range(1, i+1)):
            print("올바른 값을 입력하세요(1 ~ %d)" %(i))
            continue
        break
    index = int(index)
    index -= 1
    sel_path = path + "\\" + directories[index]

    notImg = []
    img_path = [] #이미지의 절대 경로
    file_name = [] #이미지의 이름만
    for root, subdirs, files in os.walk(sel_path): #선택 폴더 내의 모든 이미지 파일 읽어오기
        for file in files:
            if os.path.splitext(file)[1] != '.jpg' and os.path.splitext(file)[1] != '.png': #jpg, png 형식만
                notImg.append(file)
                continue
            file_name.append(file)
            img_path.append(str(root) + "\\" + str(file))

    print("중복 이미지 찾는중....")
    start = time.time() # 탐색시간 측정
    same_img_idx_list, total_cnt = get_image_hash_similarity(img_path) # 중복 이미지 탐색

    if len(same_img_idx_list) == 0:
        print("중복된 이미지가 없습니다")
        exit()

    max_resolution(same_img_idx_list, img_path) # 찾은 중복 이미지 중 최상 해상도 이미지 탐색

    print("="*30) # 찾은 중복 이미지 출력
    for j, sim in enumerate(same_img_idx_list):
        print("중복 이미지 {}".format(j+1))
        for i in sim:
            print(file_name[i], end=" | ")
        print()
    print("="*30)

    print("검사한 이미지 : {}장" .format(total_cnt), end=',  ')
    del_cnt = 0
    for li in same_img_idx_list:
        del_cnt += (len(li)-1)
    print("삭제되는 중복 이미지 : {}장" .format(del_cnt))
    print("time : %.2f s" %(time.time() - start))# 탐색시간 출력

    print("="*30)
    print("검사 예외 파일 : %d장" %(len(notImg)))
    if len(notImg) != 0:
        print(notImg)
    print("="*30)

    while True: # 삭제 여부 질의
        inp = input('삭제하시겠습니까?(y,n) : ')
        if inp == 'n':
            print("삭제 종료")
            exit()
        elif inp == 'y':
            break
        else:
            continue

    print("="*30)
    for sim in same_img_idx_list: # 삭제 부분
        for i in range(1,len(sim)): # 맨 앞 이미지(해상도 가장 높은것)를 제외(1번째부터)
            os.remove(img_path[sim[i]])
            print(file_name[sim[i]] + " 삭제")
    print("="*30)
    print("삭제가 완료 되었습니다")