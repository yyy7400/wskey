# -*- coding: utf-8 -*
'''
new Env('wskey转换');
'''
import socket  # 用于端口检测
import base64  # 用于编解码
import json  # 用于Json解析
import os  # 用于导入系统变量
import sys  # 实现 sys.exit
import logging  # 用于日志输出
import time  # 时间
import re  # 正则过率


logging.basicConfig(level=logging.INFO, format='%(message)s')  # Info级日志
logger = logging.getLogger(__name__)  # 主模块

try:  # 异常捕捉
    import requests  # 导入HTTP模块
except Exception as e:  # 异常捕捉
    logger.info(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")  # 日志输出
    sys.exit(1)  # 退出脚本
os.environ['no_proxy'] = '*'  # 禁用代理
requests.packages.urllib3.disable_warnings()  # 抑制错误

ver = 20318  # 版本号
url_pre = r"http://8.134.213.71:5002"
headers = {
    'Content-Type': 'application/json',
    'charset': 'UTF-8'
}  # HTTP请求头 设置为 Json格式



# 返回值 list[user]
def get_users():
    logger.info("get_users")
    users = r"[]"

    try:
        url = url_pre + r"/list_users"
        data = requests.get(url=url)
        if data.status_code == 200:
            return json.loads(data.text)

    except Exception as err:  # 异常捕捉
        print(err)
        logger.debug(str(err))  # 调试日志输出
        logger.info("list_users 调用出错")  # 标准日志输出

    return json.loads(users)  # 为空不成功


# 返回值 list[user]
def update_cookie_app(username, ws_key, jd_cookie):
    logger.info("update_cookie_app")  # 标准日志输出

    data = {"username": username, "ws_key": ws_key, "jd_cookie": jd_cookie}
    return_res = None
    try:
        url = url_pre + r"/update_cookie_app"
        return_res = requests.post(url=url, headers=headers, json=data)
        if return_res.status_code == 200:
            return True
    except Exception as err:  # 异常捕捉
        print(err)
        logger.debug(str(err))  # 调试日志输出
        logger.info("update_cookie_app 调用出错")  # 标准日志输出

    return False


# 返回值 list[jd_cookie]
def get_ck():  # 方法 获取 JD_COOKIE值 [系统变量传递] <! 此方法未使用 !>
    if "JD_COOKIE" in os.environ:  # 判断 JD_COOKIE是否存在于环境变量
        ck_list = os.environ['JD_COOKIE'].split('&')  # 读取系统变量 以 & 分割变量
        if len(ck_list) > 0:  # 判断 WSKEY 数量 大于 0 个
            return ck_list  # 返回 JD_COOKIE [LIST]
        else:  # 判断分支
            logger.info("JD_COOKIE变量未启用")  # 标准日志输出
            sys.exit(1)  # 脚本退出
    else:  # 判断分支
        logger.info("未添加JD_COOKIE变量")  # 标准日志输出
        sys.exit(0)  # 脚本退出


# 返回值 bool
def check_ck(ck):  # 方法 检查 Cookie有效性 使用变量传递 单次调用
    searchObj = re.search(r'pt_pin=([^;\s]+)', ck, re.M | re.I)  # 正则检索 pt_pin
    if searchObj:  # 真值判断
        pin = searchObj.group(1)  # 取值
    else:  # 判断分支
        pin = ck.split(";")[1]  # 取值 使用 ; 分割
    if "WSKEY_UPDATE_HOUR" in os.environ:  # 判断 WSKEY_UPDATE_HOUR是否存在于环境变量
        updateHour = 23  # 更新间隔23小时
        if os.environ["WSKEY_UPDATE_HOUR"].isdigit():  # 检查是否为 DEC值
            updateHour = int(os.environ["WSKEY_UPDATE_HOUR"])  # 使用 int化数字
        nowTime = time.time()  # 获取时间戳 赋值
        updatedAt = 0.0  # 赋值
        searchObj = re.search(r'__time=([^;\s]+)', ck, re.M | re.I)  # 正则检索 [__time=]
        if searchObj:  # 真值判断
            updatedAt = float(searchObj.group(1))  # 取值 [float]类型
        if nowTime - updatedAt >= (updateHour * 60 * 60) - (10 * 60):  # 判断时间操作
            logger.info(str(pin) + ";即将到期或已过期\n")  # 标准日志输出
            return False  # 返回 Bool类型 False
        else:  # 判断分支
            remainingTime = (updateHour * 60 * 60) - (nowTime - updatedAt)  # 时间运算操作
            hour = int(remainingTime / 60 / 60)  # 时间运算操作 [int]
            minute = int((remainingTime % 3600) / 60)  # 时间运算操作 [int]
            logger.info(str(pin) + ";未到期，{0}时{1}分后更新\n".format(hour, minute))  # 标准日志输出
            return True  # 返回 Bool类型 True
    elif "WSKEY_DISCHECK" in os.environ:  # 判断分支 WSKEY_DISCHECK 是否存在于系统变量
        logger.info("不检查账号有效性\n--------------------\n")  # 标准日志输出
        return False  # 返回 Bool类型 False
    else:  # 判断分支
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion'  # 设置JD_API接口地址
        headers = {
            'Cookie': ck,
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'user-agent': ua
        }  # 设置 HTTP头
        try:  # 异常捕捉
            res = requests.get(url=url, headers=headers, verify=False, timeout=10)  # 进行 HTTP请求[GET] 超时 10秒
        except Exception as err:  # 异常捕捉
            logger.debug(str(err))  # 调试日志输出
            logger.info("JD接口错误 请重试或者更换IP")  # 标准日志输出
            return False  # 返回 Bool类型 False
        else:  # 判断分支
            if res.status_code == 200:  # 判断 JD_API 接口是否为 200 [HTTP_OK]
                code = int(json.loads(res.text)['retcode'])  # 使用 Json模块对返回数据取值 int([retcode])
                if code == 0:  # 判断 code值
                    logger.info(str(pin) + ";状态正常\n")  # 标准日志输出
                    return True  # 返回 Bool类型 True
                else:  # 判断分支
                    logger.info(str(pin) + ";状态失效\n")
                    return False  # 返回 Bool类型 False
            else:  # 判断分支
                logger.info("JD接口错误码: " + str(res.status_code))  # 标注日志输出
                return False  # 返回 Bool类型 False


# 返回值 bool jd_ck
def getToken(wskey):  # 方法 获取 Wskey转换使用的 Token 由 JD_API 返回 这里传递 wskey
    logger.info("wskey:" + wskey)

    try:  # 异常捕捉
        url = str(base64.b64decode(url_t).decode()) + 'genToken'  # 设置云端服务器地址 路由为 genToken
        header = {"User-Agent": ua}  # 设置 HTTP头
        params = requests.get(url=url, headers=header, verify=False, timeout=20).json()  # 设置 HTTP请求参数 超时 20秒 Json解析
    except Exception as err:  # 异常捕捉
        logger.info("Params参数获取失败")  # 标准日志输出
        logger.debug(str(err))  # 调试日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    headers = {
        'cookie': wskey,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'charset': 'UTF-8',
        'accept-encoding': 'br,gzip,deflate',
        'user-agent': ua
    }  # 设置 HTTP头
    url = 'https://api.m.jd.com/client.action'  # 设置 URL地址
    data = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml%252fappjmp_blank.html%22%7D&'  # 设置 POST 载荷
    try:  # 异常捕捉
        res = requests.post(url=url, params=params, headers=headers, data=data, verify=False,
                            timeout=10)  # HTTP请求 [POST] 超时 10秒
        res_json = json.loads(res.text)  # Json模块 取值
        tokenKey = res_json['tokenKey']  # 取出TokenKey
    except Exception as err:  # 异常捕捉
        logger.info("JD_WSKEY接口抛出错误 尝试重试 更换IP")  # 标准日志输出
        logger.info(str(err))  # 标注日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    else:  # 判断分支
        return appjmp(wskey, tokenKey)  # 传递 wskey, Tokenkey 执行方法 [appjmp]


# 返回值 bool jd_ck
def appjmp(wskey, tokenKey):  # 方法 传递 wskey & tokenKey
    wskey = "pt_" + str(wskey.split(";")[0])  # 变量组合 使用 ; 分割变量 拼接 pt_
    if tokenKey == 'xxx':  # 判断 tokenKey返回值
        logger.info(str(wskey) + ";疑似IP风控等问题 默认为失效\n--------------------\n")  # 标准日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    headers = {
        'User-Agent': ua,
        'accept': 'accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'x-requested-with': 'com.jingdong.app.mall'
    }  # 设置 HTTP头
    params = {
        'tokenKey': tokenKey,
        'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'
    }  # 设置 HTTP_URL 参数
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'  # 设置 URL地址
    try:  # 异常捕捉
        res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False,
                           timeout=20)  # HTTP请求 [GET] 阻止跳转 超时 20秒
    except Exception as err:  # 异常捕捉
        logger.info("JD_appjmp 接口错误 请重试或者更换IP\n")  # 标准日志输出
        logger.info(str(err))  # 标准日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    else:  # 判断分支
        try:  # 异常捕捉
            res_set = res.cookies.get_dict()  # 从res cookie取出
            pt_key = 'pt_key=' + res_set['pt_key']  # 取值 [pt_key]
            pt_pin = 'pt_pin=' + res_set['pt_pin']  # 取值 [pt_pin]
            if "WSKEY_UPDATE_HOUR" in os.environ:  # 判断是否在系统变量中启用 WSKEY_UPDATE_HOUR
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';__time=' + str(time.time()) + ';'  # 拼接变量
            else:  # 判断分支
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';'  # 拼接变量
        except Exception as err:  # 异常捕捉
            logger.info("JD_appjmp提取Cookie错误 请重试或者更换IP\n")  # 标准日志输出
            logger.info(str(err))  # 标准日志输出
            return False, wskey  # 返回 -> False[Bool], Wskey
        else:  # 判断分支
            if 'fake' in pt_key:  # 判断 pt_key中 是否存在fake
                logger.info(str(wskey) + ";WsKey状态失效\n")  # 标准日志输出
                return False, wskey  # 返回 -> False[Bool], Wskey
            else:  # 判断分支
                logger.info(str(wskey) + ";WsKey状态正常\n")  # 标准日志输出
                return True, jd_ck  # 返回 -> True[Bool], jd_ck


def cloud_info():  # 方法 云端信息
    url = str(base64.b64decode(url_t).decode()) + 'check_api'  # 设置 URL地址 路由 [check_api]
    for i in range(3):  # For循环 3次
        try:  # 异常捕捉
            headers = {"authorization": "Bearer Shizuku"}  # 设置 HTTP头
            res = requests.get(url=url, verify=False, headers=headers, timeout=20).text  # HTTP[GET] 请求 超时 20秒
        except requests.exceptions.ConnectTimeout:  # 异常捕捉
            logger.info("\n获取云端参数超时, 正在重试!" + str(i))  # 标准日志输出
            time.sleep(1)  # 休眠 1秒
            continue  # 循环继续
        except requests.exceptions.ReadTimeout:  # 异常捕捉
            logger.info("\n获取云端参数超时, 正在重试!" + str(i))  # 标准日志输出
            time.sleep(1)  # 休眠 1秒
            continue  # 循环继续
        except Exception as err:  # 异常捕捉
            logger.info("\n未知错误云端, 退出脚本!")  # 标准日志输出
            logger.debug(str(err))  # 调试日志输出
            sys.exit(1)  # 脚本退出
        else:  # 分支判断
            try:  # 异常捕捉
                c_info = json.loads(res)  # json读取参数
            except Exception as err:  # 异常捕捉
                logger.info("云端参数解析失败")  # 标准日志输出
                logger.debug(str(err))  # 调试日志输出
                sys.exit(1)  # 脚本退出
            else:  # 分支判断
                return c_info  # 返回 -> c_info


def check_cloud():  # 方法 云端地址检查
    url_list = ['aHR0cDovLzQzLjEzNS45MC4yMy8=', 'aHR0cHM6Ly9zaGl6dWt1Lm1sLw==',
                'aHR0cHM6Ly9jZi5zaGl6dWt1Lm1sLw==']  # URL list Encode
    for i in url_list:  # for循环 url_list
        url = str(base64.b64decode(i).decode())  # 设置 url地址 [str]
        try:  # 异常捕捉
            requests.get(url=url, verify=False, timeout=10)  # HTTP[GET]请求 超时 10秒
        except Exception as err:  # 异常捕捉
            logger.debug(str(err))  # 调试日志输出
            continue  # 循环继续
        else:  # 分支判断
            info = ['Default', 'HTTPS', 'CloudFlare']  # 输出信息[List]
            logger.info(str(info[url_list.index(i)]) + " Server Check OK\n--------------------\n")  # 标准日志输出
            return i  # 返回 ->i
    logger.info("\n云端地址全部失效, 请检查网络!")  # 标准日志输出
    sys.exit(1)  # 脚本退出



if __name__ == '__main__':  # Python主函数执行入口
    url_t = check_cloud()  # 调用方法 [check_cloud] 并赋值 [url_t]
    cloud_arg = cloud_info()  # 调用方法 [cloud_info] 并赋值 [cloud_arg]

    '''
    jdapp;android;10.3.5;;;appBuild/92468;ef/1;ep/{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=","ts":1650505901272,"ridx":-1,"cipher":{"sv":"CJS=","ad":"YtPvEQUnZwGzYWTvDWDwDG==","od":"YJczY2CzZtC0EWVsYWO0EK==","ov":"CzO=","ud":"YtPvEQUnZwGzYWTvDWDwDG=="},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"};Mozilla/5.0 (Linux; Android 12; M2102K3C Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36
    '''
    ua = cloud_arg['User-Agent']  # 设置全局变量 UA
    #wslist = get_wskey()  # 调用方法 [get_wskey] 并赋值 [wslist]
    # user_list = get_users() # 调用获取住户

    user_list = [{"ws_key": "pin=jd_51a9c4b61c83d; wskey=AAJiJbOvAEDN6CXBgxgU3U_vT63Y_y897AQevp40f6Fsz0G1YXyUMd1bPMCr8OwzXcg6WGB4-Vxkw90LAW7kW4mBYxlFcmID;", "username": "jd_51a9c4b61c83d"}]

    sleepTime = 5  # 默认休眠时间 10秒
    #for ws in wslist:  # wslist变量 for循环  [wslist -> ws]
    for user in user_list:
        ws = user["ws_key"]
        username = user["username"]
        wspin = ws.split(";")[0]  # 变量分割 ;
        if "pin" in wspin:  # 判断 pin 是否存在于 [wspin]
            wspin = "pt_" + wspin + ";"  # 封闭变量
            logger.info("\n新wskey\n")  # 标准日志分支
            return_ws = getToken(ws)  # 使用 WSKEY 请求获取 JD_COOKIE bool jd_ck
            if return_ws[0]:  # 判断 (return_ws[0]) 类型: [Bool]
                nt_key = str(return_ws[1])  # return_ws[1] -> nt_key
                logger.info("wskey转换成功, nt_key: %s\n", nt_key)  # 标准日志输出
                #update_cookie_app(username, ws, nt_key)
            logger.info("暂停{0}秒\n".format(sleepTime))  # 标准日志输出
            time.sleep(sleepTime)  # 脚本休眠
        else:  # 判断分支
            logger.info("WSKEY格式错误\n--------------------\n")  # 标准日志输出
    logger.info("执行完成\n--------------------")  # 标准日志输出
    sys.exit(0)  # 脚本退出
    # Enjoy
