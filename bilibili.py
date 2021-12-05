import time, os
from PIL import Image, ImageEnhance


class bilibili(object):
    def __init__(self, imgsrc, ocr):
        self.imgsrc = imgsrc
        self.ocr = ocr
        self.date = time.strftime("%Y%m%d", time.localtime())

    # 分辨率统一转换成1080p
    def transfer(self, file):
        print(file)
        img = Image.open(file)
        size = img.size
        if size[0] != 1080 and size[1] != 1920:
            reim = img.resize((1080, 1920))
            reim.save(file)


    # 图片剪裁
    def cutImg(self, coordinate, imagPath):
        """
            根据坐标位置剪切图片
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
        if not os.path.exists('./dataset/bilibili_crop/' + self.date):
            os.mkdir('./dataset/bilibili_crop/' + self.date)
        imagPath = './dataset/bilibili_crop/' + self.date + '/' + source
        self.transfer(self.imgsrc)
        self.cutImg(box, imagPath)

        # 初始化
        image = Image.open(imagPath)
        size = image.size
        result = self.ocr.ocr(imagPath, cls=True)
        anchorLineWords = []
        rectangle = {}.fromkeys(['粉丝', '关注', '获赞', '编辑资料'], None)
        userInfo = {}.fromkeys(['nickName', 'fans', 'likesCount', '本人'], None)

        # 第一次遍历
        for line in result:
            # 存坐标
            if line[1][0] == '粉丝' and rectangle['粉丝'] is None:
                rectangle.update({'粉丝': line[0]})
            if line[1][0] == '关注' and rectangle['关注'] is None:
                rectangle.update({'关注': line[0]})
            if line[1][0] == '获赞' and rectangle['获赞'] is None:
                rectangle.update({'获赞': line[0]})
            if line[1][0] == '编辑资料' and rectangle['编辑资料'] is None:
                rectangle.update({'编辑资料': line[0]})
                userInfo.update({'本人': '是'})

        # 非本人
        if userInfo['本人'] is None:
            print('非本人主页')
            return None
        else:
            userInfo.pop('本人')

        # 未识别
        if rectangle['粉丝'] is None or rectangle['关注'] is None or rectangle['获赞'] is None or rectangle['编辑资料'] is None:
            print('未识别')
            return None

        # 第二次遍历, 根据坐标计算位置
        for line in result:
            # fans
            if line[0][0][0] > int(size[0] * 0.28) and line[0][1][0] < rectangle['关注'][0][0] and line[0][2][1] < rectangle['粉丝'][0][1] and line[1][0] != '粉丝' and userInfo['fans'] is None:
                userInfo.update({'fans': line[1][0]})
            # likesCount
            if line[0][0][0] > rectangle['关注'][1][0] and line[0][2][1] < rectangle['编辑资料'][1][1] and line[1][0] != '获赞' and userInfo['likesCount'] is None:
                userInfo.update({'likesCount': line[1][0]})

            if line[0][0][1] > rectangle['编辑资料'][3][1] and line[0][3][1] < rectangle['编辑资料'][3][1] + int(size[1] * 0.25):
                anchorLineWords.append(line)

        sorted(anchorLineWords, key=lambda x: x[0][0][0])
        userInfo['nickName'] = anchorLineWords[0][1][0]
        userInfo['nickName'] = userInfo['nickName'].replace("年度大会员", "")


        return userInfo


