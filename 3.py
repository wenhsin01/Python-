from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# === 設定 ChromeDriver 路徑 ===
chrome_driver_path = r"C:\Users\USER\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# === 目標網址 ===
url = "https://csie.asia.edu.tw/zh_tw/associate_professors_2"
driver.get(url)

# === 等待頁面載入 (至少等待 <body> 出現) ===
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# === 模擬滾動，確保所有動態內容載入 ===
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 為了保險起見，再等待一下
time.sleep(2)

# === 取得網頁 HTML，關閉瀏覽器 ===
html = driver.page_source
driver.quit()

# 如果需要檢查頁面結構，可將 html 寫入除錯檔案
with open("page_debug.html", "w", encoding="utf-8") as f:
    f.write(html)

# === 使用 BeautifulSoup 解析 HTML ===
soup = BeautifulSoup(html, "html.parser")

# 這裡定義四個分類（注意順序也可能影響結果）
categories = ["系主任", "教授", "榮譽教授", "兼任教授"]

# 最後要輸出的結果字串
output_text = ""

# 依據標題分區抓取內容：
# 假設網頁中各區資料由標題標示（h2、h3 或 h4），且區塊內容皆為標題後連續的兄弟元素
for cat in categories:
    output_text += f"\n{'='*10} {cat} {'='*10}\n"
    # 找到包含分類關鍵字的第一個標題
    header = soup.find(lambda tag: tag.name in ["h2", "h3", "h4"] and cat in tag.get_text())
    if header:
        section_contents = []
        # 從該標題開始，取得其後所有兄弟元素的內容，直到遇到下一個屬於其他區分類標題為止
        sibling = header.find_next_sibling()
        while sibling:
            # 若遇到新的標題且文字中包含其他分類關鍵字，則跳出該區段
            if sibling.name in ["h2", "h3", "h4"] and any(c in sibling.get_text() for c in categories):
                break
            # 若該區塊有文字，加入清理過的文字內容
            text_piece = sibling.get_text(separator="\n", strip=True)
            if text_piece:
                section_contents.append(text_piece)
            sibling = sibling.find_next_sibling()
        if section_contents:
            section_text = "\n".join(section_contents)
            output_text += section_text + "\n"
        else:
            output_text += "此區域找不到任何內容或需要調整解析方式。\n"
    else:
        output_text += "找不到該分類的標題，請檢查網頁結構。\n"

# === 儲存所有資料至 txt 檔 ===
with open("faculty_full_content.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

print("已成功抓取各分類所有內容並儲存到 faculty_full_content.txt")
