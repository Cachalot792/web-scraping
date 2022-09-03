from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
import os
import datetime
import csv

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

chart_update_day_of_the_week = 2 #Wednesday
chart_issuing_day_of_the_week = 0   #Monday

path = './billboardjapandata'

def scraping_billboard_hot_100(start_year, end_year, directory_path):

    today = datetime.date.today()
    first_date_of_the_year = datetime.date(start_year,1,1)
    offset_weekday = chart_update_day_of_the_week - first_date_of_the_year.weekday()
    if offset_weekday < 0:
        offset_weekday += 7
    first_wednesday_of_the_year = first_date_of_the_year + datetime.timedelta(offset_weekday)
    start_week = first_wednesday_of_the_year + datetime.timedelta(5)
    while True:
        if start_week < datetime.date(2008,1,21): #This is the date BillboardJapanHot100 was first published
            start_week += datetime.timedelta(7)
        else:
            break
    if end_year > today.year:
        end_year = today.year
    target_week = start_week
    target_year = start_week.year
    chart_issuing_date_of_target_week = target_week - datetime.timedelta(5)
    chart_url = 'https://www.billboard-japan.com/charts/detail?a=hot100&year=' + str(target_week.year) + '&month=' + str(target_week.month) + '&day=' + str(target_week.day)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(chart_url)

    #調査対象となっている年数分ループ
    while True:
        #CSVの初期設定
        csv_created_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file_name = 'BillboardJapanHot100_' + str(target_year) + "_" + csv_created_date + '.csv'
        csv_full_path = os.path.join(directory_path, csv_file_name)
        f = open(csv_full_path, 'w', encoding='cp932', errors='ignore')
        writer = csv.writer(f, lineterminator='\n')

        #データを取得し2次元配列を作成
        annual_data_list = []

        #1年分(約52週)ループ
        while True:
            print('ページ:' + str(chart_url))            

            #1週分(1位~100位)ループ
            error = driver.find_elements(By.ID, "error")
            if len(error) <= 0:
                element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.TAG_NAME, 'table'))
                )
                for song_title in driver.find_elements(By.XPATH, '//p[contains(@class, "musuc_title")]'):
                    artist_name = song_title.find_element(By.XPATH, '../p[@class="artist_name"]')
                    position_thisweek = song_title.find_element(By.XPATH, '../../../td[1]/span[1]')
                    position_lastweek = song_title.find_element(By.XPATH, '../../../td[1]/span[2]')
                    times_onchart = song_title.find_element(By.XPATH, '../../following-sibling::td')

                    #対象の曲のステータス設定
                    if times_onchart.text == '1':
                        song_status = 'N'
                    elif position_lastweek.text == '':
                        song_status = 'R'
                    else:
                        song_status = 'C'

                    song_detail_list = [chart_issuing_date_of_target_week, position_thisweek.text, song_status, song_title.text, artist_name.text, position_lastweek.text, times_onchart.text]
                    annual_data_list.append(song_detail_list)
            
            #ループを終了するかどうかの判断
            target_week += datetime.timedelta(7)
            chart_issuing_date_of_target_week += datetime.timedelta(7)
            if chart_issuing_date_of_target_week.year > target_year:
                target_year = target_year + 1
                break
            elif chart_issuing_date_of_target_week + datetime.timedelta(1) > today:
                target_year = target_year + 1
                break
            else:
                chart_url = 'https://www.billboard-japan.com/charts/detail?a=hot100&year=' + str(target_week.year) + '&month=' + str(target_week.month) + '&day=' + str(target_week.day)
                driver.get(chart_url)
        
        #1年分のデータを収集後CSVファイルに書き込み処理
        writer.writerows(annual_data_list)
        f.close()

        if target_year > end_year:
            break
        else:
            chart_url = 'https://www.billboard-japan.com/charts/detail?a=hot100&year=' + str(target_week.year) + '&month=' + str(target_week.month) + '&day=' + str(target_week.day)
            driver.get(chart_url)

    print('スクレイピング完了')
    driver.close()
    messagebox.showinfo('完了', 'スクレイピングが完了しました')
    quit()

scraping_billboard_hot_100(2017, 2021, path)