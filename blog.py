import time, os
from PIL import Image, ImageEnhance


class blog(object):
    def __init__(self, imgsrc, ocr):
        self.imgsrc = imgsrc
        self.ocr = ocr
        self.date = time.strftime("%Y%m%d", time.localtime())

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
        box = (0, int(size[1] * 0.08), int(size[0]), int(size[1] * 0.41))
        if not os.path.exists('./dataset/blog_crop/' + self.date):
            os.mkdir('./dataset/blog_crop/' + self.date)
        imagPath = './dataset/blog_crop/' + self.date + '/' + source
        self.cutImg(box, imagPath)

        # 初始化
        result = self.ocr.ocr(imagPath, cls=True)
        rectangle = {}.fromkeys(['关注', '粉丝', '简介'], None)
        isMyself = {}.fromkeys(['我的相册', '赞/收藏', '浏览记录', '草稿箱'], None)
        userInfo = {}.fromkeys(['nickName', 'fans', '本人'], None)

        # 第一次遍历寻找锚点存坐标
        for line in result:
            if line[1][0].find('粉丝') != -1 and rectangle['粉丝'] is None:
                rectangle.update({'粉丝': line[0]})
            if line[1][0].find('简介') != -1 and rectangle['简介'] is None:
                rectangle.update({'简介': line[0]})
            if line[1][0].find('关注') != -1 and rectangle['关注'] is None:
                rectangle.update({'关注': line[0]})
            if line[1][0].find('我的相册') != -1 and isMyself['我的相册'] is None:
                isMyself.update({'我的相册': 'exist'})
            if line[1][0].find('赞/收藏') != -1 and isMyself['赞/收藏'] is None:
                isMyself.update({'赞/收藏': 'exist'})
            if line[1][0].find('浏览记录') != -1 and isMyself['浏览记录'] is None:
                isMyself.update({'浏览记录': 'exist'})
            if line[1][0].find('草稿箱') != -1 and isMyself['草稿箱'] is None:
                isMyself.update({'草稿箱': 'exist'})

        # 非本人
        if isMyself['我的相册'] is None or isMyself['赞/收藏'] is None or isMyself['浏览记录'] is None or isMyself['草稿箱'] is None:
            print('非本人主页')
            return None
        else:
            userInfo.pop('本人')
        # 未识别
        if rectangle['简介'] is None or rectangle['粉丝'] is None or rectangle['关注'] is None:
            print('未识别')

        # 第二次遍历, 根据坐标算位置
        for line in result:
            if line[0][0][0] > (rectangle['简介'][0][0] - int(size[1] * 0.02)) and line[0][1][0] < rectangle['粉丝'][0][0] \
                    and line[0][2][1] < rectangle['简介'][0][1] and line[0][0][1] > rectangle['简介'][0][1] - \
                    int(size[1] * 0.05) and userInfo['nickName'] is None:
                userInfo['nickName'] = line[1][0]

            if line[0][0][0] > rectangle['关注'][1][0] and line[0][2][1] < rectangle['粉丝'][0][1] and line[0][0][1] > rectangle['简介'][2][1]\
                and userInfo['fans'] is None:
                userInfo['fans'] = line[1][0]

        return userInfo
