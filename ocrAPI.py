import os
import string
from urllib.parse import quote
from urllib import request
from paddleocr import PaddleOCR
from douyin import douyin
from kwai import kwai
from redbook import redbook
from blog import blog
from taobao import taobao
from dianping import dianping
from bilibili import bilibili
from wechat import wechat


class ocrAPI(object):
    """
        ocr类实例化后, 调用方法paddleOCR(url, platform), 返回一个包含个人信息的dict
        若图片不是本人主页, 则返回None, 打印 '非本人主页'
        若关键字段未能识别, 则返回None, 打印 '未能识别'
    """

    def __init__(self):
        # 启动模型
        self.ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='ch',
                        cls_model_dir='./PaddleOCR/inference/ch_ppocr_mobile_v2.0_cls_infer',
                        det_model_dir='./PaddleOCR/inference/ch_ppocr_mobile_v2.0_det_infer',
                        rec_model_dir='./PaddleOCR/inference/ch_ppocr_mobile_v2.0_rec_infer',
                        rec_char_dict_path='./PaddleOCR/ppocr/utils/ppocr_keys_v1.txt')

    def douyinImagRecognition(self, imgsrc):
        douyinUser = douyin(imgsrc, self.ocr)
        userInfo = douyinUser.ImagRecognition()
        return userInfo

    def kwaiImagRecognition(self, imgsrc):
        kwaiUser = kwai(imgsrc, self.ocr)
        userInfo = kwaiUser.ImagRecognition()
        return userInfo

    def redbookImagRecognition(self, imgsrc):
        redbookUser = redbook(imgsrc, self.ocr)
        userInfo = redbookUser.ImagRecognition()
        return userInfo

    def blogImagRecognition(self, imgsrc):
        blogUser = blog(imgsrc, self.ocr)
        userInfo = blogUser.ImagRecognition()
        return userInfo

    def taobaoImagRecognition(self, imgsrc):
        taobaoUser = taobao(imgsrc, self.ocr)
        userInfo = taobaoUser.ImagRecognition()
        return userInfo

    def dianpingImagRecognition(self, imgsrc):
        dianpinUser = dianping(imgsrc, self.ocr)
        userInfo = dianpinUser.ImagRecognition()
        return userInfo

    def bilibiliImagRecognition(self, imgsrc):
        bilibiliUser = bilibili(imgsrc, self.ocr)
        userInfo = bilibiliUser.ImagRecognition()
        return userInfo

    def wechatImagRecognition(self, imgsrc):
        wechatUser = wechat(imgsrc, self.ocr)
        userInfo = wechatUser.ImagRecognition()
        return userInfo

    def download(self, url, platform):
        imgName = url.split('/')[-1]
        if not os.path.exists('./dataset'):
            os.mkdir('./dataset')
        if not os.path.exists('./dataset/' + platform):
            os.mkdir('./dataset/' + platform)
        if not os.path.exists('./dataset/' + platform + '_crop'):
            os.mkdir('./dataset/' + platform + '_crop')
        url = quote(url, safe=string.printable)
        request.urlretrieve(url, './dataset/' + platform + '/' + imgName)
        print('Successfully downloaded')
        return './dataset/' + platform + '/' + imgName

    def paddleOCR(self, url, platform):
        imgsrc = self.download(url, platform)
        funcDict = {'douyin': self.douyinImagRecognition, 'kwai': self.kwaiImagRecognition, 'redbook': self.redbookImagRecognition, 'blog': self.blogImagRecognition,
                     'taobao': self.taobaoImagRecognition, 'dianping': self.dianpingImagRecognition, 'bilibili': self.bilibiliImagRecognition, 'wechat': self.wechatImagRecognition}

        result = funcDict.get(platform)(imgsrc)
        return result


