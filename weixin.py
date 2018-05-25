# coding:utf-8
import hashlib
import xmltodict
import time
from flask import Flask
from flask import request

WECHAT_TOKEN = 'itcast'

app = Flask(__name__)


@app.route('/weixin5000', methods=['GET','POST'])
def index():
    """验证服务器(微信和我们的服务器)地址的有效性"""

    # signature:微信加密签名，signature结合了开发者填写的token参数和请求中的timestamp参数、nonce参数。
    signature = request.args.get('signature')
    # timestamp: 时间戳
    timestamp = request.args.get('timestamp')
    # nonce:随机数
    nonce = request.args.get('nonce')
    # echostr:随机字符串
    echostr = request.args.get('echostr')

    # 1）将token、timestamp、nonce三个参数进行字典序排序
    tmp_list = [WECHAT_TOKEN, timestamp, nonce]
    tmp_list.sort()

    # 2）将三个参数字符串拼接成一个字符串进行sha1加密
    tmp_list_str = ''.join(tmp_list)
    sig = hashlib.sha1(tmp_list_str).hexdigest()

    # 3）开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    if sig == signature:
        # 能够进入这个判断，说明该请求是微信发送的
        if request.method == 'GET':
            return echostr  # 告知微信，我们的服务器准备好了
        elif request.method == 'POST':
            # 说明微信在给我们转发粉丝的消息

            # 获取微信服务器转发的粉丝的消息 xml字符串
            request_xml_str = request.data
            # 将xml字符串转成字典，方便取值
            request_xml_dict = xmltodict.parse(request_xml_str).get('xml')
            # 获取消息的类型
            msg_type = request_xml_dict.get('MsgType')

            # 判断消息的类型
            if msg_type == 'text':

                print request_xml_dict.get('Content')

                # 如果是文本消息，回一个 '你有8848吗？'
                # 封装要回的消息体
                response_xml_dict = {
                    'ToUserName': request_xml_dict.get('FromUserName'),
                    'FromUserName': request_xml_dict.get('ToUserName'),
                    'CreateTime': time.time(),
                    'MsgType': 'text',
                    'Content': u'请问有什么可以帮助您的？'
                }
                response_xml_dict = {'xml': response_xml_dict}

                # 将字典转xml字符串
                response_xml_str = xmltodict.unparse(response_xml_dict)
                # 回给微信，再由微信转给粉丝、用户
                return response_xml_str

            elif msg_type == 'voice':
                print request_xml_dict.get('Recognition')

                response_xml_dict = {
                    'ToUserName': request_xml_dict.get('FromUserName'),
                    'FromUserName': request_xml_dict.get('ToUserName'),
                    'CreateTime': time.time(),
                    'MsgType': 'text',
                    'Content': u'你说的话口音灰常重！！！'
                }
                response_xml_dict = {'xml': response_xml_dict}

                # 将字典转xml字符串
                response_xml_str = xmltodict.unparse(response_xml_dict)
                # 回给微信，再由微信转给粉丝、用户
                return response_xml_str

            elif msg_type == 'event':
                # 获取具体的事件，是关注还是取消关注
                event = request_xml_dict.get('Event')
                if event == 'subscribe':  # 表示是关注的事件
                    response_xml_dict = {
                        'ToUserName': request_xml_dict.get('FromUserName'),
                        'FromUserName': request_xml_dict.get('ToUserName'),
                        'CreateTime': time.time(),
                        'MsgType': 'text',
                        'Content': u'谢谢你的关注！！！'
                    }
                    response_xml_dict = {'xml': response_xml_dict}

                    # 获取场景值，就是二维码的参数
                    scence_id = request_xml_dict.get('EventKey')
                    if scence_id:
                        print scence_id

                    # 将字典转xml字符串
                    response_xml_str = xmltodict.unparse(response_xml_dict)
                    # 回给微信，再由微信转给粉丝、用户
                    return response_xml_str

            else:
                # 回一个'无法识别的消息'
                response_xml_dict = {
                    'ToUserName': request_xml_dict.get('FromUserName'),
                    'FromUserName': request_xml_dict.get('ToUserName'),
                    'CreateTime': time.time(),
                    'MsgType': 'text',
                    'Content': u'无法识别的消息,拜拜！'
                }
                response_xml_dict = {'xml': response_xml_dict}

                # 将字典转xml字符串
                response_xml_str = xmltodict.unparse(response_xml_dict)
                # 回给微信，再由微信转给粉丝、用户
                return response_xml_str

    return ''  # 告知微信，我们的服务器没有准备好，或者我不确定这次请求是否是你微信发送的


if __name__ == '__main__':
    app.run(debug=True, port=5000)
