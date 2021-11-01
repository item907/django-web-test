from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
from mysite import models
import pyodbc
from django.db import connection
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import datetime
import os
import twstock
#import matplotlib.pyplot as plt
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

# Create your views here.
@csrf_exempt
def index(request):
  #-->每日銀行匯率爬蟲(S)
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    r = requests.get(url)
    web = r.text
    soup = BeautifulSoup(web, 'html5lib')

    #-->標題
    title_day = soup.find(id = 'h1_small_id').text
    title_s = soup.find(id = 'h1_id').text
    title = title_day + ' ' + title_s

    #-->時間
    t_time = soup.find(class_ = 'time').text

    #-->日期
    t_day = title_day[:4] + '-' + title_day[5:7] + '-' + title_day[8:]

    #-->海關匯率用的年月旬
    yy = title_day[:4]
    mm = title_day[5:7]
    if int(title_day[8:]) > 20:
        dd = 3
    elif int(title_day[8:]) > 10:
        dd = 2
    else:
        dd = 1

    #-->幣別
    div_dollar_name = soup.find_all(class_ = 'hidden-phone print_show')

    #-->價格匯率
    div_dollar = soup.find_all(class_ = 'text-right display_none_print_show print_width')
    dollar = []
    n = 0
    for d in div_dollar:
        if n == 0:
            dollar_s = []
        dollar_s.append(d.text.strip())
        n += 1
        if n == 4:
            dollar.append(dollar_s)
            dollar_s = []
            n = 0

    n = 0
    d_r = []
    for d_n in div_dollar_name:
        d_i = []
        currency = d_n.text.strip()
        cash_buy = dollar[n][0]
        cash_sell = dollar[n][1]
        spot_buy = dollar[n][2]
        spot_sell = dollar[n][3]
        if cash_buy == '-':
            cash_buy = 0
        if cash_sell == '-':
            cash_sell = 0
        if spot_buy == '-':
            spot_buy = 0
        if spot_sell == '-':
            spot_sell = 0
        #-->另外抓出海關匯率,沒有就掛0
        try:
            bco_ex = models.BcoExrate.objects.get(year = yy, month = mm, day_r = dd, currency = currency[-4:-1])
            bco_buy = bco_ex.bco_buy
            bco_sell = bco_ex.bco_sell
        except:
            bco_buy = 0
            bco_sell = 0
        
        d_i = [currency, cash_buy, cash_sell, spot_buy, spot_sell, bco_buy, bco_sell]
        d_r.append(d_i)
        n += 1
        #-->查看資料庫有無資料，若無資料則進行寫入，有資料則做更新
        try:
            ex = models.ExrateQuery.objects.get(date = t_day, currency = currency)
            ex.cash_buy = cash_buy
            ex.cash_sell = cash_sell
            ex.spot_buy = spot_buy
            ex.spot_sell = spot_sell
            ex.save()
        except:
            ex = models.ExrateQuery.objects.create(date = t_day, currency = currency, cash_buy = cash_buy, cash_sell = cash_sell, spot_buy = spot_buy, spot_sell = spot_sell)
  #-->每日銀行匯率爬蟲(E)

  #-->掛牌匯率查詢爬蟲(S)
    if request.method == 'POST':
        try:
            q_date = request.POST['h_time'].strip()
            #-->海關匯率用的年月旬
            q_yy = q_date[:4]
            q_mm = q_date[5:7]
            if int(q_date[8:]) > 20:
                q_dd = 3
            elif int(q_date[8:]) > 10:
                q_dd = 2
            else:
                q_dd = 1
            url_query = 'https://rate.bot.com.tw/xrt/all/' + str(q_date)
            r_query = requests.get(url_query)
            web_query = r_query.text
            soup_query = BeautifulSoup(web_query, 'html5lib')

            #-->幣別
            q_d_name = soup_query.find_all(class_ = 'hidden-phone print_show')

            #-->價格匯率
            q_c_dollar = soup_query.find_all(class_ = 'phone-small-font text-right rate-content-cash print_table-cell')
            q_s_dollar = soup_query.find_all(class_ = 'phone-small-font text-right rate-content-sight print_table-cell')

            dollar_c = []
            dollar_s = []
            n = 0
            for q_c in q_c_dollar:
                if n == 0:
                    dollar_t = []
                dollar_t.append(q_c.text.strip())
                n += 1
                if n == 2:
                    dollar_c.append(dollar_t)
                    dollar_t = []
                    n = 0
            n = 0
            for q_s in q_s_dollar:
                if n == 0:
                    dollar_t = []
                dollar_t.append(q_s.text.strip())
                n += 1
                if n == 2:
                    dollar_s.append(dollar_t)
                    dollar_t = []
                    n = 0

            n = 0
            d_q_result = []
            for d_n in q_d_name:
                q_r = []
                currency = d_n.text.strip()
                cash_buy = dollar_c[n][0]
                cash_sell = dollar_c[n][1]
                spot_buy = dollar_s[n][0]
                spot_sell = dollar_s[n][1]          
                if cash_buy == '-':
                    cash_buy = 0
                if cash_sell == '-':
                    cash_sell = 0
                if spot_buy == '-':
                    spot_buy = 0
                if spot_sell == '-':
                    spot_sell = 0
                #-->查詢海關匯率,若無資料則掛0
                try:
                    q_bco = models.BcoExrate.objects.get(year = q_yy, month = q_mm, day_r = q_dd, currency = currency[-4:-1])
                    q_bco_buy = q_bco.bco_buy
                    q_bco_sell = q_bco.bco_sell
                except:
                    q_bco_buy = 0
                    q_bco_sell = 0
                q_r = [currency, cash_buy, cash_sell, spot_buy, spot_sell, q_bco_buy, q_bco_sell]
                d_q_result.append(q_r)
                n += 1

                #-->將結果寫入資料庫，以供後續排程寫入tiptop資料庫
                try:
                    ex_query = models.ExrateQuery.objects.get(date = q_date, currency = currency)
                    ex_query.cash_buy = cash_buy
                    ex_query.cash_sell = cash_sell
                    ex_query.spot_buy = spot_buy
                    ex_query.spot_sell = spot_sell
                    ex_query.save()
                except:
                    ex_query_c = models.ExrateQuery.objects.create(date = q_date, currency = currency, cash_buy = cash_buy, cash_sell = cash_sell, spot_buy = spot_buy, spot_sell = spot_sell)
                    ex_query_c.save()
        except:
            pass
    else:
        pass
  #-->掛牌匯率查詢爬蟲(E)

  #-->tiptop--apyt104假單查詢(S)
    if request.method == 'POST':
        try:
            t104_db = request.POST['t104_db'].strip()
            try:
                t104_cpf01 = request.POST['t104_cpf01'].strip()
            except:
                t104_cpf01 = ''
            try:
                t104_num = request.POST['t104_num'].strip()
            except:
                t104_num = ''
            #message = '成功'
            if t104_cpf01 == '' and t104_num == '':
                messages.add_message(request, messages.INFO, '請填上條件')
                return redirect('/')
            
            #-->抓資料庫來源(需先設定odbc)
            if t104_db == 'GE':
                db_connect = pyodbc.connect("DSN=ge1")
            elif t104_db == 'GI':
                db_connect = pyodbc.connect("DSN=gi01")
            elif t104_db == 'KS':
                db_connect = pyodbc.connect("DSN=ks01")
            elif t104_db == 'GK':
                db_connect = pyodbc.connect("DSN=gk01")
            elif t104_db == 'GZ':
                db_connect = pyodbc.connect("DSN=gz01")
            else:
                db_connect = pyodbc.connect("DSN=get1")

            
            #-->撈取單頭資料
            t104_q_list = [t104_cpf01, t104_num]
            sql = "SELECT * FROM cqg_file WHERE "
            
            n = 0
            n1 = 0
            for q in t104_q_list:
                if q != '':
                    if n == 1:
                        sql += " AND "
                    if n1 == 0:
                        sql += "cqg01 = '" + str(q) + "' "
                    if n1 == 1 :
                        sql += "cqg02 = '" + str(q) + "' "
                    n1 += 1
                n = 1

            s_d1 = ''
            for i in range(80):
                s_d1 += '='            

            cursor = db_connect.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            data1 = [[str(x).strip() for x in dt] for dt in data]
            k = ""
            for i in range(len(data1)):
                for j in range(len(data1[i])):
                    if data1[i][j] == "None":
                        data1[i].pop(j)
                        data1[i].insert(j,k)

            #-->撈取單身資料
            data2 = []
            for d in data1:
                sql2 = "SELECT * FROM cqh_file WHERE cqh01 = '"+d[0]+"' AND cqh02 = '"+d[2]+"'"
                cursor.execute(sql2)
                data = cursor.fetchall()
                data_1 = [[str(x).strip() for x in dt] for dt in data]
                data2.append(data_1)
                h = ''
                for i in range(len(data2)):
                    for j in range(len(data2[i])):
                        for k in range(len(data2[i][j])):
                            if data2[i][j][k] == "None":
                                data2[i][j].pop(k)
                                data2[i][j].insert(k,h)

            #-->將單頭單身資料做匯總
            data3 = []
            for i in range(len(data1)):
                data3_t = []
                
                #-->額外抓取--請假人姓名,部門代號,班別,部門名稱
                l_sql1 = "SELECT cpf02,cpf29,cpf30,gem02 FROM cpf_file,gem_file WHERE cpf01 = '" + data1[i][0] + "' AND gem01 = cpf29"
                cursor.execute(l_sql1)
                cpf02,cpf29,cpf30,gem02 = cursor.fetchone()
                cpf02.strip()
                cpf29.strip()
                cpf30.strip()
                gem02.strip()
                data1[i].append(cpf02)
                data1[i].append(cpf29)
                data1[i].append(cpf30)
                data1[i].append(gem02)
                
                #-->額外抓取--代理人姓名,如有颱風假...等，沒有代理人的則會出現異常
                try:
                    l_sql2 = "SELECT cpf02 FROM cpf_file WHERE cpf01 = '" + data1[i][1] + "'"
                    cursor.execute(l_sql2)
                    cpf02_1 = cursor.fetchone()[0]
                    cpf02_1.strip()
                    data1[i].append(cpf02_1)
                except:
                    cpf02_1 = ''
                    data1[i].append(cpf02_1)
                
                #-->額外抓取--假別名稱
                l_sql3 = "SELECT cpj02 FROM cpj_file WHERE cpj01 = '" + data1[i][5] + "'"
                cursor.execute(l_sql3)
                cpj02 = cursor.fetchone()[0]
                cpj02.strip()
                data1[i].append(cpj02)
                
                #-->寫入狀況名稱
                if data1[i][16] == '0':
                    msg = '開立'
                elif data1[i][16] == '1':
                    msg = '已核准'
                elif data1[i][16] == 'S':
                    msg = '送簽中'
                else:
                    msg = '送簽退回'
                data1[i].append(msg)

                data3_t.append(data1[i])
                for j in range(len(data2[i])):
                    data3_t.append(data2[i][j])
                data3.append(data3_t)
        except:
            #message = '失敗'
            message = ''
            data1 = []
            data2 = []
            data3 = []
            pass
    else:
        pass
  #-->tiptop--apyt104假單查詢(E)

  #-->股市查詢(S)
    '''
    listy = [y for y in range(1990,2101)]
    listm = [m for m in range(1,13)]
    s_yy = int(datetime.datetime.now().strftime('%Y'))
    s_mm = int(datetime.datetime.now().strftime('%m'))
    if request.method == 'POST':
        try:
            stock_type = request.POST['stock_type'].strip()
            if stock_type == 'stock_history':
                st_type_name = '單月歷史股票資料'
            elif stock_type == 'stock_realtime':
                st_type_name = '即時交易資訊'
            else:
                st_type_name = '股價'
            stock_code = request.POST['stock_code'].strip()

            #-->即時交易資訊不需取年月
            if stock_type != 'stock_realtime':
                st_y = request.POST['stock_year'].strip()
                st_m = request.POST['stock_month'].strip()
            else:
                st_y = 0
                st_m = 0

            #-->先依照代號找出公司名稱及股價
            st_name = twstock.codes[stock_code].name
            s_list = []

            if stock_type != 'stock_realtime':
                stock = twstock.Stock(stock_code)
                if stock_type == 'stock_history':
                    stock_list = stock.fetch(int(st_y),int(st_m))
                else:
                    stock_list = stock.fetch_from(int(st_y),int(st_m))

                for s in stock_list:
                    s1_date = s.date.strftime('%Y-%m-%d')
                    s1 = [s1_date, s.open, s.high, s.low, s.close]
                    s_list.append(s1)
            else:
                real = twstock.realtime.get(stock_code)
                if real['success'] == True:
                    s1_date = datetime.datetime.now().strftime('%Y-%m-%d')
                    s1 = [s1_date, real['realtime']['open'], real['realtime']['high'], real['realtime']['low'], real['realtime']['latest_trade_price']]
                    s_list.append(s1)
        except:
            pass
    else:
        pass
    '''
  #-->股市查詢(E)

  #-->今日天氣查詢(S)
    if request.method == 'POST':
        try:
            location = request.POST['c_name'].strip()

            #建立圖片字典
            dict_weather = {"多雲":"w1.png", "多雲午後短暫雷陣雨":"w2.png", "多雲時晴":"w3.png",
                            "多雲短暫陣雨":"w4.png", "晴午後短暫雷陣雨":"w5.png", "晴時多雲":"w6.png",
                            "多雲時陰":"w7.png", "多雲時陰短暫陣雨或雷雨":"w8.png", "多雲短暫陣雨或雷雨":"w9.png",
                            "陰時多雲短暫陣雨或雷雨":"w10.png", "陰短暫陣雨或雷雨":"w11.png", "陰陣雨或雷雨":"w12.png",
                            "陰時多雲陣雨或雷雨":"w13.png", "多雲時陰短暫雨":"w14.png", "陰天":"w15.png",
                            "陰時多雲短暫雨":"w16.png", "陰短暫雨":"w17.png", "多雲短暫雨":"w18.png",
                            "陰時多雲":"w19.png"}

            user_key = 'CWB-2EB84C36-A6A1-470F-BC2C-AB5544165488'
            doc_name = 'F-C0032-001'

            #由氣象局API取得氣象資料
            api_link = "http://opendata.cwb.gov.tw/opendataapi?dataid=%s&authorizationkey=%s" %(doc_name,user_key)
            report = requests.get(api_link).text
            xml_namespace = '{urn:cwb:gov:tw:cwbcommon:0.1}'
            root = et.fromstring(report)
            dataset = root.find(xml_namespace + 'dataset')
            locations_info = dataset.findall(xml_namespace + 'location')
            #取得 <location> Elements, 每個 location 就表示一個縣市資料
            target_idx = -1
            for idx, ele in enumerate(locations_info):
                locationName = ele[0].text  #取得縣市名
                if locationName == location:  #找到要查詢的縣市
                    target_idx = idx
                    break
                    #挑選出目前想要 location 的氣象資料
            tlist = ['天氣狀況','最高溫','最低溫','舒適度','降雨機率']
            showdata = []
            for i in range(len(tlist)):
                element = locations_info[target_idx][i+1]  #取出Wx(氣象描述)
                timeblock = element[1]
                data = timeblock[2][0].text
                if i == 1 or i == 2:
                    data += '°C'
                elif i == 4:
                    data += '%'
                sd = [tlist[i],data]
                if i == 0:
                    data_img = dict_weather[data]
                showdata.append(sd)
        except:
            pass
    else:
        pass
  #-->今日天氣查詢(E)

  #-->每日健康聲明(S)
    health_msg = '請依照自己當前實際情況確實做填寫'
    if request.method == 'POST':
        try:
            h_date = request.POST['health_date'].strip()
            cpf01 = request.POST['health_cpf01'].strip()
            name = request.POST['health_name'].strip()
            try:
                health = models.Health.objects.get(h_date = h_date, cpf01 = cpf01, name = name)
                if health.h_date != '' or health.cpf01 != '' or health.name != '':
                    health_msg = '今日已填寫'
            except:
                phone = request.POST['health_phone'].strip()
                status = request.POST['status'].strip()
                status0 = request.POST['status0'].strip()
                status1 = request.POST['status1'].strip()
                status2 = request.POST['status2'].strip()
                if status == 'Y' and status0 == '':
                    health_msg = '如有發燒...等情況，需填寫症狀描述'
                else:
                    health = models.Health.objects.create(h_date = h_date, cpf01 = cpf01, name = name, phone = phone, status = status, status0 = status0, status1 = status1, status2 = status2)
                    health.save()
                    health_msg = '填寫完畢'
        except:
            pass
  #-->每日健康聲明(E)

    return render(request, 'index.html', locals())
    #return render(request, 'debug.html', locals())

def tiptop_ex_create(request):
    #-->取得資料庫內最近一日
    date_q = models.ExrateQuery.objects.values('date').distinct().aggregate(Max('date'))
    date = str(date_q['date__max'])
    # date = '2021-03-12'
    date1 = date[:4] + '/' + date[5:7] + '/' + date[8:]
    yy = date[:4]
    mm = date[5:7]
    if int(date[8:]) > 20:
        dd = 3
    elif int(date[8:]) > 10:
        dd = 2
    else:
        dd = 1

    #-->連線資料庫(暫定只更新台北資料)
    db_connect = pyodbc.connect("DSN=ge1")
    cursor = db_connect.cursor()

    #-->先查詢當天是否有資料,有資料則不寫入
    cnt = ''
    q_sql = "SELECT COUNT(*) FROM tc_azk_file WHERE tc_azk01 = '" + date1 + "'"
    cursor.execute(q_sql)
    cnt = cursor.fetchone()[0]
    if cnt == 0:
        try:
            ex_data = models.ExrateQuery.objects.filter(date = date)
            for d in ex_data:
                date1 = str(d.date)[:4] + '/' + str(d.date)[5:7] + '/' + str(d.date)[8:]
                tc_azk01 = date1
                tc_azk02 = str(d.currency[-4:-1])
                tc_azk03 = str(d.cash_buy)
                tc_azk04 = str(d.cash_sell)
                tc_azk05 = str(d.spot_buy)
                tc_azk06 = str(d.spot_sell)

                #-->撈取海關匯率
                try:
                    bco = models.BcoExrate.objects.get(year = yy, month = mm, day_r = dd, currency = tc_azk02)
                    tc_azk07 = str(bco.bco_buy)
                    tc_azk08 = str(bco.bco_sell)
                except:
                    tc_azk07 = '0'
                    tc_azk08 = '0'

                #-->因tiptop人民幣代號為RMB,故額外做轉換
                if tc_azk02 == 'CNY':
                    tc_azk02 = 'RMB'

                c_sql = "INSERT INTO tc_azk_file VALUES('" + tc_azk01 + "','" + tc_azk02 + "','" + tc_azk03 + "','" + tc_azk04 + "','" + tc_azk05 + "','" + tc_azk06 + "','" + tc_azk07 + "','" + tc_azk08 + "');"
                cursor.execute(c_sql)
                db_connect.commit()
        except:
            pass
    else:
        pass
    db_connect.close()
    return redirect('/')
    #return render(request, 'debug.html', locals())

def bco_ex(request):
    #-->取條件(預設執行當天的年月日)
    date = datetime.datetime.now()
    yy = str(date.year)
    if date.month < 10:
        mm = '0' + str(date.month)
    else:
        mm = str(date.month)
    if date.day > 20:
        dd = str(3)
    elif date.day > 10:
        dd = str(2)
    else:
        dd = str(1)

    #-->利用selenium模擬實際查詢情況
    driverPath = r"C:\Users\Administrator\Desktop\chromedriver.exe"
    driver = webdriver.Chrome(driverPath)
    url = "https://portal.sw.nat.gov.tw/APGQO/GC331"
    driver.get(url)
    time.sleep(5)

    #-->填上查詢條件,做查詢
    year = Select(driver.find_element_by_id("yearList"))
    month = Select(driver.find_element_by_id("monList"))
    day = Select(driver.find_element_by_id("tenDayList"))
    year.select_by_value(yy)
    month.select_by_value(mm)
    day.select_by_value(dd)
    query = driver.find_element_by_id("queryButton")
    query.click()

    #-->解析查詢後的網頁
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,"html5lib")
    div = soup.find_all(class_ = 'ui-widget-content jqgrow ui-row-ltr')

    d3 = []
    for d in div:
        d1 = d.find_all('td')
        d2 = [d.text for d in d1]
        d3.append(d2)

    #-->將結果寫入資料庫,若已有對應結果則做更新
    for bco in d3:
        try:
            bco_ex = models.BcoExrate.objects.get(year = yy, month = mm, day_r = dd, currency = bco[3])
            bco_ex.bco_buy = bco[7]
            bco_ex.bco_sell = bco[8]
            bco_ex.save()
        except:
            bco_ex = models.BcoExrate.objects.create(year = yy, month = mm, day_r = dd, currency = bco[3], bco_buy = bco[7], bco_sell = bco[8])

    #-->關掉selenium及cmd
    driver.close()
    d_close = "taskkill /f /im chromedriver.exe"
    os.system(d_close)
    return redirect('/')
    #return render(request, 'debug.html', locals())