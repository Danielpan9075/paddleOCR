import time, re, os
from PIL import Image, ImageEnhance


class dianping(object):
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
        box = (0, int(size[1] * 0.085), int(size[0]), int(size[1] * 0.5))
        if not os.path.exists('./dataset/dianping_crop/' + self.date):
            os.mkdir('./dataset/dianping_crop/' + self.date)
        imagPath = './dataset/dianping_crop/' + self.date + '/' + source
        self.cutImg(box, imagPath)

        # 初始化
        result = self.ocr.ocr(imagPath, cls=True)
        image = Image.open(imagPath)
        size = image.size
        anchorLineWords = []
        rectangle = {}.fromkeys(['粉丝', '关注', '总浏览量', '昵称'], None)
        userInfo = {}.fromkeys(['nickName', 'fans', 'level', 'area', '本人'], None)

        # 第一次遍历
        for line in result:
            # 存坐标
            if line[1][0] == '粉丝' and rectangle['粉丝'] is None:
                rectangle.update({'粉丝': line[0]})
            if line[1][0] == '关注' and rectangle['关注'] is None:
                rectangle.update({'关注': line[0]})
            if line[1][0] == '总浏览量' and rectangle['总浏览量'] is None:
                rectangle.update({'总浏览量': line[0]})

        # 未识别
        if rectangle['粉丝'] is None or rectangle['关注'] is None or rectangle['总浏览量'] is None:
            print('未识别')
            return None

        # 第二次遍历, 根据坐标识别所需信息
        for line in result:
            # 昵称、地区
            if int(size[0] * 0.24) < line[0][0][0] < rectangle['关注'][1][0]:
                if len(anchorLineWords) == 0:
                    anchorLineWords.append(line)
                    rectangle.update({'昵称': line[0]})
                elif len(anchorLineWords) > 0 and line[0][0][1] > rectangle['昵称'][3][1] and line[0][3][1] < \
                        rectangle['昵称'][3][1] + int(size[1] * 0.095) and userInfo['area'] is None:
                    if line[1][0].split(' ', 1)[0][-1] in ('男', '女'):
                        userInfo['area'] = line[1][0].split(' ', 1)[0][:-1]
                    else:
                        userInfo['area'] = line[1][0].split(' ', 1)[0]
            # 等级
            if rectangle['昵称'] is not None and line[0][0][0] > rectangle['昵称'][1][0] and line[0][0][1] < rectangle['昵称'][2][1] \
                and line[0][2][1] > rectangle['昵称'][1][1]:
                anchorLineWords.append(line)

            # 粉丝
            if line[0][1][0] < int(size[0] / 4) and line[0][2][1] < rectangle['粉丝'][0][1] and line[0][0][1] > \
                    rectangle['粉丝'][0][1] - int(size[1] * 0.124) and userInfo['fans'] is None:
                userInfo.update({'fans': line[1][0]})

            # 本人
            if (line[1][0] == '关注' or line[1][0] == '发消息') and line[0][0][1] > rectangle['粉丝'][2][1]:
                userInfo.update({'本人': '否'})
                return None

        # 拆分过滤 昵称、等级
        sorted(anchorLineWords, key=lambda x: x[0][0][0])
        if len(anchorLineWords) == 1:
            userInfo['nickName'] = anchorLineWords[0][1][0].split('Lv', 1)[0].split('（', 1)[0].split(' ', 1)[0]

            try:
                userInfo['level'] = anchorLineWords[0][1][0].split('Lv', 1)[1]
            except:
                userInfo['level'] = None
        else:
            userInfo['nickName'] = anchorLineWords[0][1][0]
            pattern = re.compile(r'\D')
            userInfo['level'] = re.sub(pattern, '', anchorLineWords[1][1][0])

        userInfo.pop('本人')
        return userInfo
