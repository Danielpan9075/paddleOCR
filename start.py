import sys, os
from ocrAPI import ocrAPI
from aiohttp import web

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


async def postOCR(request):
    try:
        try:
            data = await request.json()
        except:
            data = {}
        print('postCommodityCategory start ==> {} {} {}'.format(
            request.url, data, request.transport.get_extra_info('peername')))

        try:
            url = data['url']
            platform = data['platform']
        except:
            url = ""
            platform = ""
        if not data:
            return web.json_response({
                "code": -1,
                "message": "失败",
                "data": "参数不全"
            })
        usr_info = recognizer.paddleOCR(url, platform)
        rsp = {
            "code": 1,
            "message": "成功",
            "data": usr_info
        }
        return web.json_response(rsp)

    except Exception as e:
        rsp = {
            "code": -1,
            "message": "失败",
            "data": str(e),
        }
        print('postOCR error ==> {} {}'.format(
            request.transport.get_extra_info('peername'), str(e)))
        return web.json_response(rsp)


app = web.Application()
app.router.add_post('/ocr', postOCR)


if __name__ == '__main__':
    recognizer = ocrAPI()
    web.run_app(app, host='0.0.0.0', port=5001)
