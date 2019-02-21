from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from selenium.webdriver.common.action_chains import ActionChains
from pyquery import PyQuery as pq
from lxml import etree
from bs4 import BeautifulSoup
import time
import pymongo
chrome_option=webdriver.ChromeOptions()
# chrome_option.add_argument('--proxy-server=127.0.0.1:8080')
browser=webdriver.Chrome(options=chrome_option)
browser.maximize_window()
wait=WebDriverWait(browser,10)
KEYWORD='小米手机'
url='https://www.jd.com/'

def soso():
    browser.get(url)
    sou=wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,'#key')
        ))
    sousub=wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR,'#search > div > div.form > button')
        ))
    sou.send_keys(KEYWORD)
    sousub.click()
    time.sleep(5)

    print("正在爬取第1页！！！")
    xinxi()
    main()
def xinxi():
    try:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        html = browser.page_source
        # html = etree.HTML(html)
        soup=BeautifulSoup(html,'lxml')
        # items = html.xpath('//li[@class="gl-item"]')
        i=0
        for item in soup.select('#J_goodsList > ul > li'):
            print(item)
            if item.select('div > div.p-img > a > img')[0].attrs['data-lazy-img'] != "done":   #判断是否存在图片地址
                img=item.select('div > div.p-img > a > img')[0].attrs['data-lazy-img']
            else:
                img =item.select('div > div.p-img > a > img')[0].attrs['src']  #获取图片地址
                price=item.select('div > div.p-price > strong')[0].text   #获取价格
            deal=item.select('div > div.p-commit > strong')[0].text    #获取交易量
            title=item.select('div > div.p-name.p-name-type-2 > a > em')[0].text   #获取标题
            try:shop=item.select('div > div.p-shop > span > a')[0].text    #获取店铺信息
            except Exception:shop="null"
            product={
                "img":img,
                "price":price,
                "deal":deal,
                "title":title,
                "shop":shop,
            }
            print(product)
            save_mongo(product)
            i += 1
            print(i)
            print('****************************************************************************************************************************')
    except Exception:
        xinxi()
       
def main():
    for page in range(2,102):
        next_page(page)
def next_page(page):
    print("正在爬取第", page, "页！！！")
    try:
        if page > 1:
            next = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next')
            ))
            next.click()
           
        time.sleep(5)
        xinxi()
    except TimeoutException:
        next_page(page)

def save_mongo(result):  #保存到Mongodb
    MONGO_URL='localhost'
    MONGO_DB='jd'
    MONGO_COLLECTION='product'
    client=pymongo.MongoClient(MONGO_URL)
    db=client[MONGO_DB]
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到Mongodb成功！')
    except Exception:
        print('存储到Mongodb失败!')


if __name__=="__main__":
    soso()

