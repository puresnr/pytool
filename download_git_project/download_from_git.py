#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 脚本用于下载指定gitlab服务器下，所有某个用户可以访问的项目

import  requests
from urllib.parse import urlencode
import  os
from subprocess import run
import configparser

print( '******************************\n如果提示找不到模块，使用pip3安装对应的模块\neg: pip3 install urllib\n调用git clone进行下载，使用前需要配置好git\n******************************')

conf = configparser.ConfigParser()
conf.read('cfg.ini', encoding='utf-8')

os.chdir(conf.get('config', 'local_path'))

url = 'https://%s/api/v4/projects?' % conf.get('config', 'host')

param = {'private_token': conf.get('config', 'token'), 'simple': True, 'per_page': 100, 'page': 1}
for item in conf.items('filter'):
    if len(item[1]) != 0:
        param[item[0]] = item[1]

result = 'complete'

while True:
    print(url + urlencode(param))
    res  =  requests.get(url + urlencode(param),  headers=None,  verify=False)
    if res.status_code != 200:
        result = 'request failed at ' + url + urlencode(param)
        break
        
    pro  =  res.json()
    for  p  in  pro:
            print(p.get('name')  +  '  '  +  p.get('ssh_url_to_repo'))
            run('git  clone  '  +  p.get('ssh_url_to_repo')  +  '  '  +  conf.get('config', 'local_path')  +  '/'  +  p.get('path_with_namespace'), shell = True)
    if len(pro) != param['per_page']:
        break
    param['page'] += 1

print(result)
