
# -*- coding: utf-8 -*-

'''
该脚本从国务院新闻发布平台搜索关于国内假期安排的通知，下载处理后生成国内法定节假日安排，是第一手的权威数据
目前只处理了初始放假安排的通知，没有处理变动假期安排的通知，假如假期产生了变动，只能做到通知维护人，由维护人手动处理
'''
 
import urllib.request
from urllib.parse import quote
import random
import re
import datetime
import json
import sys
import time
from bs4 import BeautifulSoup

''' 
#@获取403禁止访问的网页 
'''  
my_headers=["Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",  
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"  
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",  
"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"]

def getContent(url, host, referer):  
    req=urllib.request.Request(url)  
    req.add_header("User-Agent",random.choice(my_headers))  
    req.add_header("Host", host)  
    req.add_header("Referer", referer)
    req.add_header("GET",url)  
    return urllib.request.urlopen(req).read()  

def commonHoliday(year, bs):
    print('**************** year:', year, '****************')
    finalTexts = []
    for p in bs.find_all('p'):
        texts = p.get_text().split("：")
        if len(texts) == 1:
            continue
        for t in texts:
            fts = re.split('[一二三四五六七八九十]、', t)
            finalTexts.extend(fts)

    holidays = {}
    for i in range(0, len(finalTexts)):
        tobj = re.match('([0-9]*)年([0-9]*)月([0-9]*)日.([0-9]*)年([0-9]*)月([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d to %04d-%02d-%02d' % (int(tobj.group(1)) , int(tobj.group(2)), int(tobj.group(3)), int(tobj.group(4)), int(tobj.group(5)),int(tobj.group(6)))
            continue

        tobj = re.match('([0-9]*)年([0-9]*)月([0-9]*)日.([0-9]*)月([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d to %04d-%02d-%02d' % (int(tobj.group(1)) , int(tobj.group(2)), int(tobj.group(3)), int(tobj.group(1)), int(tobj.group(4)), int(tobj.group(5)))
            continue

        tobj = re.match('([0-9]*)年([0-9]*)月([0-9]*)日.([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d to %04d-%02d-%02d' % (int(tobj.group(1)) , int(tobj.group(2)), int(tobj.group(3)),int(tobj.group(1)) , int(tobj.group(2)), int(tobj.group(4)))
            continue

        tobj = re.match('([0-9]*)月([0-9]*)日.([0-9]*)月([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d to %04d-%02d-%02d' % (int(year), int(tobj.group(1)) , int(tobj.group(2)), int(year), int(tobj.group(3)), int(tobj.group(4)))
            continue

        tobj = re.match('([0-9]*)月([0-9]*)日.([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d to %04d-%02d-%02d' % (int(year), int(tobj.group(1)) , int(tobj.group(2)), int(year), int(tobj.group(1)), int(tobj.group(3)))
            continue
        tobj = re.match('([0-9]*)年([0-9]*)月([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d' % (int(tobj.group(1)) , int(tobj.group(2)), int(tobj.group(3)))
            continue
        tobj = re.match('([0-9]*)月([0-9]*)日', finalTexts[i])
        if tobj:
            holidays[finalTexts[i - 1]] = '%04d-%02d-%02d' % (int(year), int(tobj.group(1)) , int(tobj.group(2)))
            continue
       
    for k in holidays.keys():
        print(k, ":", holidays[k])
    print('********************************************')

def downloadFile(url):
    bs = BeautifulSoup(getContent(url, "www.gov.cn", "http://sousuo.gov.cn/").decode('utf-8'), "html.parser")

    tobj = re.match('国务院办公厅关于(.*)年部分节假日安排的通知', bs.title.string)
    if tobj:
        commonHoliday(tobj.group(1), bs)
    else:
        print('Unknown file type! Send mail now!')    # TODO: 未识别的通知类型，发送邮件给维护人处理

def genQueryFilesUrl(start, end, cnt):
    return '%s&mintime=%s&maxtime=%s&n=%d' % ('http://sousuo.gov.cn/data?t=zhengce_gw&q=%s&timetype=timezd&searchfield=title&pcodeJiguan=%s&puborg=&pcodeYear=&pcodeNum=&filetype=&p=&sort=score' % (quote('假'.encode('utf-8')), quote('国办发明电'.encode('utf-8'))), start, end, cnt)

def queryFiles(start, end):
    host = "sousuo.gov.cn"
    referer = "http://sousuo.gov.cn/a.htm?t=zhengce"

    for file in json.loads(getContent(genQueryFilesUrl(start, end, json.loads(getContent(genQueryFilesUrl(start, end, 1), host, referer))['searchVO']['totalCount']), host, referer))['searchVO']['listVO']:
        downloadFile(file['url'])

def main():
    print('说明：可以通过参数设置查询日期范围\n示例：\n***.py ---- 查询所有\n***.py 2020-01-01 ---- 查询 2020-01-01 至 今日 的数据\n***.py 2020-01-01 2021-01-01 ---- 查询 2020-01-01 至 2021-01-01 的数据\n')

    start = end = ''
    if len(sys.argv) == 3:
       start = sys.argv[1]
       end = sys.argv[2]
    elif len(sys.argv) == 2:
        start = sys.argv[1]
        end = time.strftime("%Y-%m-%d", time.localtime())

    queryFiles(start, end)

if __name__ == '__main__':
    main()
