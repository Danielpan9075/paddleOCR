import time, re, os
from PIL import Image, ImageEnhance


class kwai(object):
    def __init__(self, imgsrc, ocr):
        self.imgsrc = imgsrc
        self.ocr = ocr
        self.date = time.strftime("%Y%m%d", time.localtime())

    # 判断数字
    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    # 分辨率统一转换为1080p
    def transfer(self, file):
        img = Image.open(file)
        size = img.size
        if size[0] != 1080 and size[1] != 1920:
            reim = img.resize((1080, 1920))
            reim.save(file)

    # 图片剪裁
    def cutImg(self, coordinate, imagPath):
        """根据坐标位置剪切图片
        :param imgsrc: 原始图片路径(str)
        :param coordinate: 原始图片上的坐标(tuple) egg:(x, y, w, h) ---> x,y为矩形左上角坐标, w,h为右下角坐标
        :param imagPath: 剪切输出图片路径(str)
        :return: None
        """
        image = Image.open(self.imgsrc)
        region = image.crop(coordinate)
        # 亮度增强
        # region = ImageEnhance.Brightness(region).enhance(1.5)
        # 色度增强
        region = ImageEnhance.Color(region).enhance(1.5)
        # 对比度增强
        region = ImageEnhance.Contrast(region).enhance(1.5)
        # 锐度增强
        region = ImageEnhance.Sharpness(region).enhance(3.0)
        region.save(imagPath)

    # 图片识别
    def ImagRecognition(self):
        """
            根据坐标位置剪切图片
            :param  imgsrc: 原始图片路径(str)
            :return userInfo: 用户信息 dict
            """

        # 切割掉背景图
        image = Image.open(self.imgsrc)
        size = image.size
        source = self.imgsrc.split('/')[-1]
        box = (0, int(size[1] * 0.17), int(size[0]), int(size[1]))
        if not os.path.exists('./dataset/kwai_crop/' + self.date):
            os.mkdir('./dataset/kwai_crop/' + self.date)
        imagPath = './dataset/kwai_crop/' + self.date + '/' + source
        self.cutImg(box, imagPath)
        self.transfer()

        # 初始化
        result = self.ocr.ocr(imagPath, cls=True)
        rectangle = {}.fromkeys(['用户ID'], None)
        userInfo = {}.fromkeys(['nickName', 'userId', 'fans', '本人'], None)
        userInfo['nickName'] = ''

        # 第一次遍历
        for r in result:
            # 用户ID
            if r[1][0].find('用户ID') != -1 or r[1][0].find('快手号') != -1:
                rectangle['用户ID'] = r[0]
                pattern = re.compile(r'[(用户ID|快手号)：\u4e00-\u9fa5^>]')
                userInfo.update({'userId': re.sub(pattern, "", r[1][0])})
            #粉丝
            if r[1][0].find('粉丝') != -1 and userInfo['fans'] is None:
                # pattern = re.compile(r'\d+.*W*')
                # userInfo['粉丝'] = re.findall(pattern, r[1][0].strip().split('粉丝', 1)[0])
                userInfo['fans'] = ''
                fans = r[1][0].strip().split('粉丝', 1)[0]
                for i in fans:
                    if self.isNumber(i) or i == '.' or i == 'W':
                        userInfo['fans'] += i
                    else:
                        break
            if r[1][0].find('完善资料') != -1:
                userInfo['本人'] = '是'

        # 是否本人
        if userInfo['本人'] is None:
            print('非本人主页')
            return None
        else:
            userInfo.pop('本人')

        # 未识别
        if rectangle['用户ID'] is None:
            print('未识别')
            return None

        # 第二次遍历, 根据坐标计算所需字段内容
        for line in result:
            # 昵称
            if rectangle['用户ID'][2][1] - int(size[1] * 0.05) < line[0][2][1] < rectangle['用户ID'][2][1]:
                userInfo['nickName'] += line[1][0]

        return userInfo
