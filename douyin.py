import time, re, os
from PIL import Image, ImageEnhance


class douyin(object):
    def __init__(self, imgsrc, ocr):
        self.imgsrc = imgsrc
        self.ocr = ocr
        self.date = time.strftime("%Y%m%d", time.localtime())

    # 分辨率统一转换成1080p
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
        # region = ImageEnhance.Color(region).enhance(1.5)
        # 对比度增强
        # region = ImageEnhance.Contrast(region).enhance(1.5)
        # 锐度增强
        # region = ImageEnhance.Sharpness(region).enhance(3.0)
        region.save(imagPath)

    # 图片识别
    def ImagRecognition(self):

        # 切割掉背景图
        image = Image.open(self.imgsrc)
        size = image.size
        source = self.imgsrc.split('/')[-1]
        box = (0, int(size[1] * 0.1), int(size[0]), int(size[1]))
        if not os.path.exists('./dataset/douyin_crop/' + self.date):
            os.mkdir('./dataset/douyin_crop/' + self.date)
        imagPath = './dataset/douyin_crop/' + self.date + '/' + source
        self.cutImg(box, imagPath)
        self.transfer(imagPath)

        # 初始化
        result = self.ocr.ocr(imagPath, cls=True)
        image = Image.open(imagPath)
        size = image.size
        rectangle = {}.fromkeys(['抖音号', '获赞', '关注', '粉丝'], None)
        userInfo = {}.fromkeys(['nickName', 'userId', 'likesCount', 'fans', '本人'], None)
        userInfo['nickName'] = ''

        # 第一次遍历
        for line in result:
            # 存抖音号及关键字坐标
            if line[1][0].find('抖音号') != -1:
                rectangle.update({'抖音号': line[0]})
                pattern = re.compile(r'[抖音号：\u4e00-\u9fa5]')
                userInfo.update({'userId': re.sub(pattern, "", line[1][0])})
            if line[1][0] == '获赞' and rectangle['获赞'] is None:
                rectangle.update({'获赞': line[0]})
            if line[1][0] == '关注' and rectangle['关注'] is None:
                rectangle.update({'关注': line[0]})
            if line[1][0] == '粉丝' and rectangle['粉丝'] is None:
                rectangle.update({'粉丝': line[0]})
            if line[1][0].find('编辑资料') != -1 or line[1][0].find('添加朋友') != -1:
                userInfo.update({'本人': '是'})

        # 非本人
        if userInfo['本人'] is None:
            print('非本人主页')
            return None
        else:
            userInfo.pop('本人')

        # 未识别
        if rectangle['抖音号'] is None or rectangle['获赞'] is None or rectangle['关注'] is None or rectangle['粉丝'] is None:
            print('未识别')
            return None

        # 第二次遍历, 根据坐标计算所需字段内容
        for line in result:
            if line[0][0][0] > rectangle['获赞'][0][0] - int(size[0] * 0.08) and line[0][1][0] < int(size[0] * 0.5) \
                    and line[0][3][1] < rectangle['获赞'][3][1] + int(size[1] * 0.05) and line[0][0][1] > rectangle['获赞'][3][1] and userInfo['likesCount'] is None:
                userInfo.update({'likesCount': line[1][0]})

            if line[0][3][1] < rectangle['粉丝'][3][1] + int(size[1] * 0.05) and line[0][0][1] > rectangle['粉丝'][3][1] \
                    and rectangle['粉丝'][0][0] < int((line[0][0][0] + line[0][1][0]) / 2) < rectangle['粉丝'][1][0] and userInfo['fans'] is None:
                userInfo.update({'fans': line[1][0]})

            if line[0][2][1] < rectangle['抖音号'][1][1] and line[0][0][1] > rectangle['抖音号'][0][1] - int(size[1] * 0.07):
                userInfo['nickName'] += line[1][0]

        return userInfo

