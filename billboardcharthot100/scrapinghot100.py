from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
import os
import datetime
import csv
import numpy as np

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

chart_update_day_of_the_week = 1 #火曜日
chart_issuing_day_of_the_week = 5   #土曜日

path = 'C:/Users/shito/Documents/billboarddata'
delimiter = '/d/e/l/i/m/i/t/e/r/'

def scraping_billboard_hot_100(start_year, end_year, directory_path):

    first_date_of_the_year = datetime.date(start_year,1,1)
    offset_weekday = chart_update_day_of_the_week - first_date_of_the_year.weekday()
    if offset_weekday < 0:
        offset_weekday += 7
    first_tuesday_of_the_year = first_date_of_the_year + datetime.timedelta(offset_weekday)
    start_week = first_tuesday_of_the_year + datetime.timedelta(4)
    target_week = start_week
    target_year = start_year
    chart_url = 'https://www.billboard.com/charts/hot-100/' + str(target_week) + '/'
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(chart_url)
    print('ページ:' + str(chart_url))

    #調査対象となっている年数分ループ
    while True:
        #CSVの初期設定
        csv_chart_year = str(target_year)
        csv_created_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file_name = 'BillboardHot100_' + csv_chart_year + "_" + csv_created_date + '.csv'
        csv_full_path = os.path.join(directory_path,csv_file_name)
        f = open(csv_full_path, 'w', encoding='cp932', errors='ignore')
        writer = csv.writer(f, lineterminator='\n')

        #データを取得し2次元配列を作成
        heading_column_list = []
        heading_column_list.append('Rank')
        for num in range(100):
            heading_column_list.append(num + 1)
        annual_data_list = [heading_column_list]

        #1年分(約52週)ループ
        while True:
            one_week_chart_list = []
            one_week_chart_list.append(target_week)

            #1週分(1位~100位)ループ
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'chart-results-list'))
            )
            for song_title in driver.find_elements(By.XPATH, '//ul[contains(@class, "o-chart-results-list-row")]//h3'):
                artist_name = song_title.find_element(By.XPATH, 'following-sibling::span')
                position_lastweek = song_title.find_element(By.XPATH, '../../li[4]/span')
                times_onchart = song_title.find_element(By.XPATH, '../../li[6]/span')

                #対象の曲のステータス設定
                if times_onchart.text == '1':
                    song_status = 'N'
                elif position_lastweek.text == '-':
                    song_status = 'R'
                else:
                    song_status = 'C'

                song_detail = song_title.text + str(delimiter) + artist_name.text + str(delimiter) + position_lastweek.text + str(delimiter) + times_onchart.text + str(delimiter) + str(song_status)
                one_week_chart_list.append(song_detail)

            annual_data_list.append(one_week_chart_list)
            
            #ループを終了するかどうかの判断
            target_week = target_week + datetime.timedelta(days=7)
            if target_week.year > target_year:
                target_year = target_year + 1
                break
            elif target_week > datetime.date.today() + datetime.timedelta(days=abs(chart_issuing_day_of_the_week - chart_update_day_of_the_week) - 1):
                target_year = target_year + 1
                break
            else:
                chart_url = 'https://www.billboard.com/charts/hot-100/' + str(target_week) + '/'
                driver.get(chart_url)
                print('ページ:' + str(chart_url))
        
        #1年分のデータを収集後、リストの行列を入れ替えてCSVファイルに書き込み処理
        one_year_chart_list = np.array(annual_data_list).T
        writer.writerows(one_year_chart_list)
        f.close()

        if target_year > end_year:
            break
        else:
            chart_url = 'https://www.billboard.com/charts/hot-100/' + str(target_week) + '/'
            driver.get(chart_url)
            print('ページ:' + str(chart_url))

    print('スクレイピング完了')
    messagebox.showinfo('完了', 'スクレイピングが完了しました')
    driver.close()
    quit()

scraping_billboard_hot_100(2022, 2022, path)