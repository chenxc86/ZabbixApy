# -*- coding:utf8 -*-

# 作者：chenxc
#
# 联系：chenxc@bokecc.com
#
# 日期：2014.12.25
#
# 描述：
#
# 模块对Zabbix Api进行了封装，给予Zabbix Documentation 2.2。
#
# 运行环境：
#
# Zabbix Server 2.2.1
#
# Python version 2.x.x

import urllib2
import json


class AuthError(Exception):
    """Zabbix Server认证异常
    """
    def __init__(self, error_data):
        Exception.__init__(self)
        self.error_data = error_data

    def __str__(self):
        return repr(self.error_data)


class PostJson(object):
    """Api 超类
    """
    ContentType = {"Content-Type": "application/json"}

    def __init__(self, uri):
        self.uri = uri

    def _http_request(self, api_request_data):
        """HTTP POST请求，POST数据为JSON格式，将响应的JSON数据解析为字典。
        """
        # 构造http请求对象。
        json_encoded_data = json.dumps(api_request_data)
        request = urllib2.Request(self.uri, json_encoded_data)
        for key, value in PostJson.ContentType.items():
            request.add_header(key, value)

        # 发送POST请求到Api
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
           # print "URLError, Please Check Your URL:", e
            print e
            return False
        result = json.loads(response.read())
        response.close()
        return result


class ZAP(PostJson):
    """封装了Zabbix Server Api
    """
    def __init__(self, uri, username, password):
        """实例构造方法
        """
        PostJson.__init__(self, uri)
        self.zabbix_user = username
        self.zabbix_password = password
        self.api_data = dict(jsonrpc="2.0", method="", params="", id=0)

    def login_zabbix(self):
        """Zabbix Server登录认证
        """
        self.api_data["method"] = "user.login"
        self.api_data["params"] = dict(user=self.zabbix_user, password=self.zabbix_password)

        result = self._http_request(self.api_data)
        if "error" in result.keys():
            raise AuthError(result["error"]["data"])

        self.api_data["auth"] = result["result"]
        self.api_data["id"] = 1

    def logout_zabbix(self):
        """Zabbix Server登出清楚session
        """
        self.api_data["method"] = "user.logout"
        self.api_data["params"] = list()
        return self._http_request(self.api_data)


    def req_zabbix_api(self, method, params):
        """发送请求至Zabbix Server
        """
        self.api_data["method"] = method
        self.api_data["params"] = params

        return self._http_request(self.api_data)
