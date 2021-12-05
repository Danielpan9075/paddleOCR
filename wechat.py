import time, os
from PIL import Image, ImageEnhance


class wechat(object):
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
        box = (0, int(size[1] * 0.8), int(size[0]), int(size[1]))
        if not os.path.exists('./dataset/wechat_crop/' + self.date):
            os.mkdir('./dataset/wechat_crop/' + self.date)
        imagPath = './dataset/wechat_crop/' + self.date + '/' + source
        self.cutImg(box, imagPath)

        # 初始化
        result = self.ocr.ocr(imagPath, cls=True)
        # image = Image.open(imagPath)
        # size = image.size
        rectangle = {}.fromkeys(['微信', '通讯录', '发现', '我', '好友数'], None)
        userInfo = {}.fromkeys(['fansCount', '本人'], None)

        for line in result:
            if line[1][0] == '微信' and rectangle['微信'] is None:
                rectangle.update({'微信': line[0]})
            if line[1][0] == '通讯录' and rectangle['通讯录'] is None:
                rectangle.update({'通讯录': line[0]})
            if line[1][0] == '发现' and rectangle['发现'] is None:
                rectangle.update({'发现': line[0]})
            if line[1][0] == '我' and rectangle['我'] is None:
                rectangle.update({'我': line[0]})
            if line[1][0].find('个朋友') != -1:
                rectangle.update({'好友数': line[0]})
                userInfo['fansCount'] = int(line[1][0].strip().split('个朋友', 1)[0])

        # 非本人
        if rectangle['微信'] is None or rectangle['通讯录'] is None or rectangle['发现'] is None or rectangle['我'] is None or rectangle['好友数'] is None:
            print('非本人主页或未识别')
            return None
        else:
            userInfo.pop('本人')

        return userInfo


