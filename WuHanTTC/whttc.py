"""
Created on 2024/12/2 下午8:32 
Author: Shuijing
Description: 武汉TTT学习平台刷课工具
"""
import time

import requests

qi = int(input('请输入您需要刷的期数,3=全部:'))
# 输入完整 cookie 字符串
cookie_str = input('请输入您的cookie,需要复制全部cookie:\n')

# 把 cookie 字符串转成字典
cookies = {}
for item in cookie_str.split(';'):
    if '=' in item:
        k, v = item.strip().split('=', 1)
        cookies[k] = v

# 修改或新增字段
cookies['MaxTimeLength_932'] = '12332'
cookies['TheMaxTime'] = '12332'
cookies['MaxTimeLength_967'] = '12332'
cookies['MaxTimeLength_917'] = '12332'
cookies['MaxTimeLength_1976'] = '12332'
cookies['MaxTimeLength_1918'] = '12332'

print(cookies)

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Origin': 'http://nsstudy.whttc.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15',
    'Referer': 'http://nsstudy.whttc.com/kj/ViewPlay.aspx?xl=1&id=932',
    'Upgrade-Insecure-Requests': '1',
    # 'Content-Length': '394',
    'Connection': 'keep-alive',
    # 'Cookie': 'MaxTimeLength_932=0; TheMaxTime=0; MaxTimeLength_967=0; MaxTimeLength_917=0; MaxTimeLength_1976=0; LocalStudyProgress_1918=D00BGwQWVmVTTVlIRzxdRUBHESYRUFNRRWZWTUtIRytbXVdHAA4YAktJRWhSQl9XXGoKAwIHQxI%3D; MaxTimeLength_1918=0; ASP.NET_SessionId=w3nv1w3r3tuoiyaz4eubsctc; SavedLogin=UserName=421126199108057009&Userid=10764',
    'Priority': 'u=0, i',
}

data = {
    '__VIEWSTATE': 'waWLDjUJQ5rDNN080R+Mo08AjJVxiqaEgdf4Mw+39zv4xzE2HGQiwhObvEjXCs4YY5bW72bBC+QzF4I94wMmGUOYaFpR4oT/FqO9mTPUysVQ9AlknemUh9aCy0kTasL5US8IyA==',
    '__VIEWSTATEGENERATOR': '5620F3FD',
    '__EVENTVALIDATION': 'TQq4lj3nsmCoZ076HkwzZs/jsO+AZ28OR482dFtwFUCh9vLegHBzp2vYvL/FNZuqQq1bSYXC0efQsbGx3V/+PUyPS0x4ejeEv+oaTGffIk4Z2so0JeVWIo9C1mLkjOB4n6EnecPcjVPKHCw49WqGq7dxRtY=',
    'Button1': 'Button',
}


def shuake(start, end):
    """刷课函数，接受起始和结束id"""
    for i in range(start, end + 1):
        params = {
            'xl': '1',
            'id': i,
        }
        attempt = 0  # 尝试次数
        while attempt < 5:  # 最多尝试5次
            attempt += 1
            try:
                response = requests.post('http://nsstudy.whttc.com/kj/ViewPlay.aspx', params=params, cookies=cookies,
                                         headers=headers, data=data)
                # 检查是否是运行时错误
                if "运行时错误" in response.text:
                    print(f"第{i}期：出现运行时错误，重试第{attempt}次...")
                    time.sleep(2)  # 等待 2 秒后重试
                    continue  # 继续重试
                else:
                    print(i, response.text)  # 打印成功返回的内容
                    break  # 成功则退出重试
            except requests.RequestException as e:
                print(f"第{i}期：请求出错，错误信息：{e}，重试第{attempt}次...")
                time.sleep(2)  # 请求异常时，等待 2 秒后重试

        if attempt == 5:
            print(f"第{i}期：尝试了5次，仍然出现错误，跳过此期。")

        time.sleep(2)  # 请求之间稍作延时


if qi == 1:
    # 更新为新的课程ID范围
    shuake(917, 967)  # 假设新课程范围，可以根据实际情况调整
    print('刷完2期')

if qi == 2:
    shuake(1918, 1976)
    print('刷完1期')

if qi == 3:
    shuake(917, 967)  # 更新为新课程范围
    print('刷完1期')
    shuake(1918, 1976)
    print('刷完2期')
    print('全部刷完')
