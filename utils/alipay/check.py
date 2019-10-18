#!/usr/bin/env python
# -*- coding:utf8 -*-

# pip install pycryptodome   需要模块加密方面的模块
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    """支付宝支付成功后通知接口验证"""

    # 接收支付宝支付成功后，向我们设置的同步支付通知url，请求的参数
    return_url = 'http://47.92.87.172:8000/?total_amount=100.00&timestamp=2017-10-11+22%3A44%3A17&sign=dHW%2F25EDd%2BYKqkU5krhseDNIOEyDpdJzSAaoqhTC0nlv8%2FEmrQVd0WqgGK0CS8Pax8sK4jIOdGLFa6lQEbIfzvH3Na2W949yCAYX04JL1Bi02wog7a8L7vfW9Kj%2BjfTQxumGH%2B1Drbezdg9gKOx3tX0cb1yBBdfifK6l1%2BE5UjggGbY60F6SD8A8XI06NMWb4ViU%2FLYtBhwAwU2koy1IK2%2BtBJM1xYFuBRlcWF61xCxexHwO0WEA3AwVRW1miuJjOpGiBTOwPI9Huj0WhkyRebIjBhSxReJdZIdTfAgwj4oqo4jAJCHDa6DKBM0H3wjKKXSyMeMBGKQB0Uv2rNdyng%3D%3D&trade_no=2017101121001004320200174640&sign_type=RSA2&auth_app_id=2016080800192023&charset=utf-8&seller_id=2088102170418468&method=alipay.trade.page.pay.return&app_id=2016080800192023&out_trade_no=201702021227&version=1.0'

    # 将同步支付通知url,传到urlparse
    o = urlparse(return_url)
    # 获取到URL的各种参数
    query = parse_qs(o.query)
    # 定义一个字典来存放，循环获取到的URL参数
    processed_query = {}
    # 将URL参数里的sign字段拿出来
    ali_sign = query.pop("sign")[0]

    # 传递参数初始化支付类
    alipay = AliPay(
        appid="2016101200665303",                                   # 设置签约的appid
        app_notify_url="http://140.143.237.146:80/",                  # 异步支付通知url
        app_private_key_path=u"ying_yong_si_yao.txt",               # 设置应用私钥
        alipay_public_key_path="zhi_fu_bao_gong_yao.txt",           # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,                                   # 设置是否是沙箱环境，True是沙箱环境
        return_url="http://140.143.237.146:80/"                      # 同步支付通知url
    )

    # 循环出URL里的参数
    for key, value in query.items():
        # 将循环到的参数，以键值对形式追加到processed_query字典
        processed_query[key] = value[0]
    # 将循环组合的参数字典，以及拿出来的sign字段，传进支付类里的verify方法，返回验证合法性，返回布尔值，True为合法，表示支付确实成功了，这就是验证是否是伪造支付成功请求
    print(alipay.verify(processed_query, ali_sign))

# 如果别人伪造支付成功请求，它不知道我们的支付宝公钥，伪造的就无法通过验证，测试可以将支付宝公钥更改一下，在验证就会失败，别忘了改回来