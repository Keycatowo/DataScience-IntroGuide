import requests
from bs4 import BeautifulSoup
from dagster import asset, get_dagster_logger
import pandas as pd
import datetime

@asset
def url():
    """爬蟲目標網址"""
    return "https://ithelp.ithome.com.tw/users/20140721/ironman/4944"
    
@asset
def views_lsit(url):
    """爬取30天瀏覽數"""
    logger = get_dagster_logger() # 這裡的 logger 是 Dagster 提供的物件，可以用來記錄資訊
    headers = {
        'content-type': 'text/html; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    all_views = []
    for page_i in range(1, 4):
        res = requests.get(url, params={"page": page_i}, headers=headers)
        if res.status_code != 200:
            logger.error(f"Request fail, status code: {res.status_code}")
            raise Exception(f"Request fail, status code: {res.status_code}")
        soup = BeautifulSoup(res.text, 'lxml')
        qa_condition_count = soup.find_all("span", {"class": "qa-condition__count"})
        qa_condition_count = [int(i.text) for i in qa_condition_count]
        views = qa_condition_count[2::3]
        logger.info(f"Page {page_i} views: {views}")
        all_views.extend(views)
    return all_views

@asset
def views_record():
    """讀取瀏覽數紀錄"""
    logger = get_dagster_logger()
    # 檢查檔案是否存在，若不存在則建立一個空的 DataFrame
    try:
        df_views = pd.read_csv("views_data.csv")
        logger.info(f"Read views record: {df_views}")
    except:
        logger.warning("No views record")
        df_views = pd.DataFrame(columns=["日期"] + [f"{i}" for i in range(1, 31)])
    return df_views

@asset
def today():
    """取得今天日期，格式為yyyy/mm/dd"""
    logger = get_dagster_logger()
    today_str = datetime.date.today().strftime("%Y/%m/%d")
    logger.info(f"Today: {today_str}")
    return today_str


@asset
def add_views_record(views_record, views_lsit, today):
    """新增一筆今天的資料"""
    views_record.loc[len(views_record)] = [today] + views_lsit
    return views_record

@asset
def save_views_record(add_views_record):    
    """儲存瀏覽數紀錄"""
    logger = get_dagster_logger()
    logger.info(f"Save views record: {len(add_views_record)} rows")
    add_views_record.to_csv("views_data.csv", index=False)
    return None