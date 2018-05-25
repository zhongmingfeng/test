# -*- coding:utf-8 -*-
# 生成二维码

from flask import Flask
import time
import urllib2
import json


# 目前使用的测试账号的，实际开发需要使用正式账号的
APPID = 'wx8686603852286d55'
APPSECRET = 'dde296c4ef4cc1c5a3c014f0397c63ba'


app = Flask(__name__)


class AccessToken():
    """刷新access_token
    封装一段独立的逻辑，获取全局唯一变量
    """

    # 定义成私有的，是了不让外界在没有任何判断的前提下，就访问aaccess_token
    _access_token = {
        # 封装到一个字典中，是为了统一的管理，高内聚
        'access_token':'',
        'expires_in':7200,
        'create_time':time.time()
    }

    # 定义成类方法，是为了通过类名就能访问get_access_token，
    # 避免实例方法访问前，需要实例化新的对象，在实例化过程中对_access_token有干扰的
    @classmethod
    def get_access_token(cls):
        """获取私有的_access_token的入口
        方便我们在这里对access_token进行一个校验，判断是否为空或者是否过期，,只有通过校验后才能返回access_token
        """
        # {"access_token":"ACCESS_TOKEN","expires_in":7200} {"errcode":40013,"errmsg":"invalid appid"}

        acs = cls._access_token

        if not acs.get('access_token') or (time.time() - acs.get('create_time') > acs.get('expires_in')):

            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPID, APPSECRET)
            response_json_str = urllib2.urlopen(url).read()
            response_json_dict = json.loads(response_json_str)

            # 判断是否错误
            if 'errcode' in response_json_dict:
                raise Exception(response_json_dict.get('errmsg'))
            else:
                cls._access_token['access_token'] = response_json_dict.get('access_token')
                cls._access_token['expires_in'] = response_json_dict.get('expires_in')
                cls._access_token['create_time'] = time.time()

        return cls._access_token['access_token']


@app.route('/<scene_id>')
def index(scene_id):
    """
    1.使用access_token获取ticket
    2.使用ticket获取二维码图片
    """

    # 1.使用access_token获取ticket
    # 获取ticket的URL
    url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s' % AccessToken.get_access_token()
    # 准备请求体
    params_dict = {
        "expire_seconds": 604800,
        "action_name": "QR_SCENE",
        "action_info": {"scene": {"scene_id": scene_id}}
    }
    params_str = json.dumps(params_dict)
    # 发送请求获取ticket
    response_json_str = urllib2.urlopen(url, data=params_str).read()
    response_json_dict = json.loads(response_json_str)
    # 获取票据
    ticket = response_json_dict.get('ticket')

    # 2.使用ticket获取二维码图片
    url_qr = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s' % ticket
    return '<img src="%s">' % url_qr


if __name__ == '__main__':
    app.run(debug=True)


# if __name__ == '__main__':
#     print AccessToken.get_access_token()
#     print AccessToken.get_access_token()