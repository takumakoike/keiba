import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# 全体のURL
base_url = os.environ["BASE_URL"]
# レースのURL
race_base_url = os.environ["RACE_BASE_URL"]


# 全体のページから各レースページに遷移するリンクを取得
page_data = requests.get(base_url)
soup = bs(page_data.content, "html.parser")
all_links = soup.select('td.result > a')


# リンクごとに情報を取得し、CSVに書き込み
for href in all_links:
    text = href.get('href')
    result_url = race_base_url + text

    req = requests.get(result_url)
    soup = bs(req.content, "html.parser")
    # レースタイトル
    race_title = soup.select("div.cell.date")[0].text

    # レース結果
    race_headers = soup.select("thead")
    race_results = soup.select("tbody")
    race_headers_rows = race_headers[0].find_all("tr")
    rows = race_results[0].find_all("tr")
    header = ["レースタイトル"] + [cell.get_text(strip=True) for cell in race_headers[0].find_all(["th", "td"])]


    data = [
        [
            cell.find('img')['src'].rsplit('/', 1)[-1].rsplit('.', 1)[0]
            if cell.has_attr('class') and 'waku' in cell['class'] and cell.find('img')
            else cell.get_text(strip=True)
            for cell in row.find_all(['th', 'td'])
        ]
        for row in rows
    ]

    data_with_new_column = [
        [race_title] + row
        for row in data
    ]

    df = pd.DataFrame(data_with_new_column)
    csv_file = os.environ["CSV_FILE_PATH"]

    # 最初の書き込み時はヘッダーを含める
    if not os.path.exists(csv_file):
        # ファイルが存在しない場合はヘッダー付きで書き込む
        df.to_csv(csv_file, mode="w", index=False, header=True, encoding="utf-8")
    else:
        # ファイルが存在する場合はヘッダーなしで追記
        df.to_csv(csv_file, mode="a", index=False, header=False, encoding="utf-8")