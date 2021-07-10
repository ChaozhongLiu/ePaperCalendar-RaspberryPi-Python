#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
# sys.path.append(r'../lib')

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath + "/lib")

import epd5in83_V2
import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont,ImageChops, ImageOps
import traceback
import datetime
import requests
import logging
import math
from icalendar import Calendar, Event

#timeUpdate = datetime.datetime.now()
#logtime = timeUpdate.strftime('%Y-%m-%d') #年月日
#log_writer = open('log_%s.txt'%(logtime),'w')

fontYMDSize = ImageFont.truetype(rootPath + '/lib/QiHei.ttf', 25)
fontLunarSize = ImageFont.truetype(rootPath + '/lib/LangSong.ttf', 25)
fontCitySize = ImageFont.truetype(rootPath + '/lib/ZhiHei.ttf', 30)
fontDateSize = ImageFont.truetype(rootPath + '/lib/YiCha.ttf', 160)
fontWeekSize = ImageFont.truetype(rootPath + '/lib/LangSong.ttf', 30)
fontTipSize = ImageFont.truetype(rootPath + '/lib/ZiZai.ttf', 30)
fontTempSize = ImageFont.truetype(rootPath + '/lib/LangSong.ttf', 25)

oilStrTime = ""
weekStr = ""
oilStrWeek = ""
countUpdate_1 = False
countUpdate_2 = False
countUpdate_3 = False
countUpdate_4 = False
#SwitchDay = True
weatherTextToday = "" #[""]*2
#weatherTextTomorrow = [""]*2
weatherIconToday = ""
#weatherIconTomorrow = ""
tempArray = ["--"]*5
health_tips = ""

#农历日历ics
g = open('../lib/chinese_lunar_2021-05-01_2025-12-31.ics','r')
cal = Calendar.from_ical(g.read())
lunarDate = ""

def getTime():
    return(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"   ")
    #天气
    #r = requests.get('https://devapi.qweather.com/v7/weather/now?key=38ccc24a1d4b4c8da60e9e941d21ad1c&location=101180101')
    #r = requests.get('https://devapi.qweather.com/v7/air/now?key=38ccc24a1d4b4c8da60e9e941d21ad1c&location=101180101')
    #健康小贴士
    #r = requests.get('http://api.tianapi.com/txapi/healthtip/index?key=62a28b9609b82125d917c9600b9ec02b')

    #获取天气
    '''
    天气数据示例
    {'code': '200', 'updateTime': '2021-06-10T16:57+08:00', 'fxLink': 'http://hfx.link/2qk1', 
    'now': {'obsTime': '2021-06-10T16:44+08:00', 
            'temp': '32', 
            'feelsLike': '32', 
            'icon': '101', 
            'text': '多云', 
            'wind360': '90', 
            'windDir': '东风', 
            'windScale': '3', 
            'windSpeed': '16', 
            'humidity': '41', 
            'precip': '0.0', 
            'pressure': '992', 
            'vis': '17', 
            'cloud': '91', 
            'dew': '15'}, 
        'refer': {'sources': ['Weather China'], 'license': ['no commercial use']}}
    '''
    '''
    空气数据示例
    {'code': '200', 'updateTime': '2021-06-10T16:58+08:00', 'fxLink': 'http://hfx.link/2qk4', 
        'now': {'pubTime': '2021-06-10T16:00+08:00', 
            'aqi': '115', 
            'level': '3', 
            'category': '轻度污染', 
            'primary': 'O3', 'pm10': '102', 'pm2p5': '25', 'no2': '14', 'so2': '5', 'co': '0.8', 'o3': '230'},
        'station':[]}
    '''
    '''
    健康贴士示例
    {'code': 200, 'msg': 'success', 'newslist': [{'content': '每天都吃鱼，且吃鱼应多于其他家禽。'}]}
    '''
lunarDic = {'初二': 1, '初三': 2, '初四': 3, '初五': 4, '初六': 5, '初七': 6, '初八': 7, '初九': 8, '初十': 9, 
'十一': 10, '十二': 11, '十三': 12, '十四': 13, '十五': 14, '十六': 15, '十七': 16, '十八': 17, '十九': 18, '二十': 19, 
'廿一': 20, '廿二': 21, '廿三': 22, '廿四': 23, '廿五': 24, '廿六': 25, '廿七': 26, '廿八': 27, '廿九': 28, '三十': 29}

def get_Lunar():
    today = datetime.date.today()
    entries = [dict(summary=event['SUMMARY']) for event in cal.walk('VEVENT') if event['DTSTART'].dt <= today < event['DTEND'].dt]
    lunarDate = str(entries[0]['summary'])
    lunarDate = lunarDate.split(' ')
    if len(lunarDate[0]) > 2:
        if len(lunarDate) == 2:
            lunarDate = lunarDate[0] + '初一 ' + lunarDate[1]
        elif len(lunarDate) == 1:
            lunarDate = lunarDate[0] + '初一 '
    else:
        chuYi = today - datetime.timedelta(days = lunarDic[lunarDate[0]])
        entries = [dict(summary=event['SUMMARY']) for event in cal.walk('VEVENT') if event['DTSTART'].dt <= chuYi < event['DTEND'].dt]
        lunarMonth = str(entries[0]['summary'])
        lunarMonth = lunarMonth.split(' ')[0]
        if len(lunarDate) == 2:
            lunarDate = lunarMonth + ' ' + lunarDate[0] + ' ' + lunarDate[1]
        elif len(lunarDate) == 1:
            lunarDate = lunarMonth + ' ' + lunarDate[0]
    return lunarDate



def getTemp():                                                                   # 连接超时,6秒，下载文件超时,7秒
    r = requests.get('https://devapi.qweather.com/v7/weather/now?key=38ccc24a1d4b4c8da60e9e941d21ad1c&location=101180101',timeout=(6,7))
    r.encoding = 'utf-8'
    r2 = requests.get('https://devapi.qweather.com/v7/air/now?key=38ccc24a1d4b4c8da60e9e941d21ad1c&location=101180101',timeout=(6,7))
    r2.encoding = 'utf-8'

    print(getTime()+'状态码: '+str(r.status_code), flush=True)
    if r.status_code == 200:
        print(getTime()+'1-服务器正常!', flush=True)
    elif r.status_code == 404:
        print(getTime()+'1-网页不存在!', flush=True)
        return
    elif r.status_code == 500:
        print(getTime()+'1-服务器错误!', flush=True)
        return

    print(getTime()+'状态码: '+str(r2.status_code), flush=True)
    if r2.status_code == 200:
        print(getTime()+'2-服务器正常!', flush=True)
    elif r2.status_code == 404:
        print(getTime()+'2-网页不存在!', flush=True)
        return
    elif r2.status_code == 500:
        print(getTime()+'2-服务器错误!', flush=True)
        return

    try:
        tempList = [
        ('郑州'),                                     #城市
        (r.json()['now']['feelsLike']),              #体感温度
        (r.json()['now']['icon']),                   #天气图标
        (r.json()['now']['text']),                   #天气文本
        (r2.json()['now']['category'])               #空气质量
        ]
    except:
        tempList = ["--"]*5
        print(getTime()+'获取天气数据失败...', flush=True)
        return tempList
    else:
        print(getTime()+'获取天气数据成功...', flush=True)
        return tempList

def GetTip():
    r = requests.get('http://api.tianapi.com/txapi/healthtip/index?key=62a28b9609b82125d917c9600b9ec02b',timeout=(6,7))
    r.encoding = 'utf-8'

    print(getTime()+'状态码: '+str(r.status_code), flush=True)
    if r.status_code == 200:
        print(getTime()+'3-服务器正常!', flush=True)
    elif r.status_code == 404:
        print(getTime()+'3-网页不存在!', flush=True)
        return
    elif r.status_code == 500:
        print(getTime()+'3-服务器错误!', flush=True)
        return

    try:
        health_tips = r.json()['newslist'][0]['content']
    except:
        health_tips = ""
        print(getTime()+'获取天气数据失败...', flush=True)
        return health_tips
    else:
        print(getTime()+'获取天气数据成功...', flush=True)
        return health_tips




def UpdateWeatherText(tempArray):
    TextTemp = tempArray[3]
    '''
    if(len(TextTemp)<2):
        strtemp = tempArray[TodayTomorrow]
        TextTemp = [""]*2
        TextTemp[0] = strtemp[0:5]
        TextTemp[1] = strtemp[5:]
    '''
    return TextTemp

def UpdateWeatherIcon(tempType):  #匹配天气类型图标
    '''
    if(tempType == "大雨"  or tempType == "中到大雨"):
        return "大雨.bmp"
    elif(tempType == "暴雨"  or tempType == "大暴雨" or 
        tempType == "特大暴雨" or tempType == "大到暴雨" or
        tempType == "暴雨到大暴雨" or tempType == "大暴雨到特大暴雨"):
        return "暴雨.bmp"
    elif(tempType == "沙尘暴" or tempType == "浮尘" or
        tempType == "扬沙" or tempType == "强沙尘暴" or
        tempType == "雾霾"):
        return "沙尘暴.bmp"
    '''
    return (tempType + ".bmp")
        
def todayWeek(nowWeek):
    if nowWeek == "0":
        return"星期天"
    elif nowWeek =="1":
        return"星期一"
    elif nowWeek =="2":
        return"星期二"
    elif nowWeek =="3":
        return"星期三"
    elif nowWeek =="4":
        return"星期四"
    elif nowWeek =="5":
        return"星期五"
    elif nowWeek =="6":
        return"星期六"

def UpdateData():
    tempArray = getTemp()
    global weatherTextToday
    global weatherIconToday
    weatherTextToday = UpdateWeatherText(tempArray)
    weatherIconToday = UpdateWeatherIcon(tempArray[2])
    return tempArray


#348 ~ 640 像素 居中显示
#居中显示的方法 一个字宽度30像素 例如重479像素开始 多加一个字 少空 15 个像素
def alignCenter(string,scale,startPixel):
    charsCount = 0
    for s in string:
        charsCount += 1
    charsCount *= scale/2
    charsCount = startPixel - charsCount
    return charsCount

#切分长句子
def chunks(health_tips):
    chunk_list = []
    n = math.floor(len(health_tips) / 12)
    for i in range(n):
        chunk_list.append(health_tips[12*i:12*i+12])
    chunk_list.append(health_tips[12*n:])
    for i in range(len(chunk_list)):
        tmp_slice = chunk_list[i]
        if tmp_slice.startswith('，'):
            tmp_slice.lstrip('，')
        elif tmp_slice.startswith(','):
            tmp_slice.lstrip(',')
        elif tmp_slice.startswith('。'):
            tmp_slice.lstrip('。')
        elif tmp_slice == '，' or tmp_slice == '，' or tmp_slice == '，':
            chunk_list = chunk_list[0:i]
    return chunk_list

#刷新循环
while (True):
    print(getTime()+'start...', flush=True)
    epd = epd5in83_V2.EPD()
    epd.init()

    timeUpdate = datetime.datetime.now()
    strtime = timeUpdate.strftime('%Y-%m-%d') #年月日
    strtime2 = timeUpdate.strftime('%H:%M')   #时间
    strtime3 = timeUpdate.strftime('%M')      #分钟
    strtime4 = timeUpdate.strftime('%w')      #星期
    strtime5 = timeUpdate.strftime('%H')      #小时
    strtime6 = timeUpdate.strftime('%d')      #日期
    
    epd.Clear()
    
    if(strtime4 != oilStrWeek):  #每天重置更新天气
        oilStrWeek = strtime4
        countUpdate_1 = True
        '''
        countUpdate_2 = True
        countUpdate_3 = True
        countUpdate_4 = True
        '''
        tempArray = UpdateData()
        lunarDate = get_Lunar()
        weekStr = todayWeek(strtime4)
        print(getTime()+'重置更新天气', flush=True)

    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    #print(epd.height, epd.width)

  
    #左上显示年月日
    draw.text((20, 20), strtime, font = fontYMDSize, fill = 0)

    #左上显示农历
    draw.text((20, 60), lunarDate, font = fontLunarSize, fill = 0)

    #右上显示城市
    draw.text((370, 20), tempArray[0], font = fontCitySize, fill = 0)
    #draw.text((110, 335), tempArray[8] + "更新", font = fontTempSize, fill = 0)

    #居中显示日 - 数字
    draw.text((alignCenter(strtime6,75,230), 150), strtime6, font = fontDateSize, fill = 0)
    #居中显示星期
    draw.text((alignCenter(weekStr,25,230), 300), weekStr, font = fontWeekSize, fill = 0)


    #显示图标
    #bmp = Image.open(rootPath + '/pic/icon.png')
    #Himage.paste(bmp,(15,80))

    # 更新天气信息
    intTime = int(strtime5)
    tempArray = UpdateData()
    epd.Clear()
    print(getTime()+strtime2 + '更新天气', flush=True)

    #每日更新一次健康贴士
    if countUpdate_1:
        health_tips = GetTip()
        #health_tips = "幼儿不宜经常服用止咳糖浆。"
        health_tips = chunks(health_tips)
        countUpdate_1 = False
        print(getTime()+strtime2 + '更新贴士', flush=True)
    '''
    elif(countUpdate_2 and intTime == 11):
        tempArray = UpdateData()
        countUpdate_2 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    elif(countUpdate_3 and intTime == 16):
        tempArray = UpdateData()
        countUpdate_3 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    elif(countUpdate_4 and intTime == 21 ):
        tempArray = UpdateData()
        countUpdate_4 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    '''
    #居中下部显示贴士
    for i in range(len(health_tips)):
        draw.text((alignCenter(health_tips[i],30,230),380+35*i), health_tips[i], font = fontTipSize, fill = 0)
    #draw.text((alignCenter(health_tips,30,240),400), health_tips, font = fontTipSize, fill = 0)
 
    #底部显示
    #天气 #显示空气质量 #显示温度 (显示℃ )
    temp_F = tempArray[1] + '度'
    #tempTypeIcon = Image.open(rootPath + "/pic/weatherType/" + weatherIconToday)
    #tempTypeIcon = ImageOps.invert(tempTypeIcon.convert('RGB'))
    #Himage.paste(tempTypeIcon,(20,550))
    TempText = tempArray[3] + ' / ' + "空气质量 "+ tempArray[4] + ' / ' + "体感温度 "+ temp_F
    draw.text((45,600), TempText, font = fontTempSize, fill = 0)


    
    '''
    if(SwitchDay):#天气滚动
        draw.text((348,90),"今日：", font = fontTempSize, fill = 0) 
        #显示天气图标
        tempTypeIcon = Image.open(rootPath + "/pic/weatherType/" + weatherIconToday)
        Himage.paste(tempTypeIcon,(450,90))
        draw.text((alignCenter(tempArray[9],30,479),177),tempArray[9], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextToday[0],30,479),225),weatherTextToday[0], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextToday[1],30,479),266),weatherTextToday[1], font = fontTempSize, fill = 0)
        SwitchDay = False
    else:
        draw.text((348,90),"明日：", font = fontTempSize, fill = 0)
        tempTypeIcon = Image.open(rootPath + "/pic/weatherType/" + weatherIconTomorrow)
        Himage.paste(tempTypeIcon,(450,90))
        draw.text((alignCenter(tempArray[11],30,479),177),tempArray[11], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextTomorrow[0],30,479),225),weatherTextTomorrow[0], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextTomorrow[1],30,479),266),weatherTextTomorrow[1], font = fontTempSize, fill = 0)
        SwitchDay = True
    '''

    #画竖线(x开始值，y开始值，x结束值，y结束值)
    #draw.rectangle((325, 90, 326, 290), fill = 0)
    #画横线
    #draw.rectangle((0, 315, 680, 317), fill = 0)
    #刷新屏幕
    print(getTime()+strtime2 + '刷新屏幕...', flush=True)
    Himage = ImageChops.invert(Himage)
    epd.display(epd.getbuffer(Himage))
    #屏幕休眠
    epd.sleep()
    print(getTime()+strtime2 + '屏幕休眠...', flush=True)
    if(intTime >= 1 and intTime <= 6): #2点～6点 每小时刷新一次
        time.sleep(3600)
    else:
        time.sleep(1800)




