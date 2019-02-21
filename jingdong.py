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
            # print(item.xpath('//div[@class="p-img"]//img')[i].get('src'))
            # print(item.select('div > div.p-img > a > img')[0].attrs['src'])
            # print(item.select('div > div.p-img > a > img'))
            print(item)
            if item.select('div > div.p-img > a > img')[0].attrs['data-lazy-img'] != "done":
                img=item.select('div > div.p-img > a > img')[0].attrs['data-lazy-img']
            else:
                img =item.select('div > div.p-img > a > img')[0].attrs['src']
                price=item.select('div > div.p-price > strong')[0].text
            deal=item.select('div > div.p-commit > strong')[0].text
            title=item.select('div > div.p-name.p-name-type-2 > a > em')[0].text
            try:shop=item.select('div > div.p-shop > span > a')[0].text
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
        # print(item.xpath('//div[@class="p-img"]//img').get('src'))
        # if item.xpath('//div[@class="p-img"]//img')[i].get('data-lazy-img') != "done":
        #     product = {
        #         "img:":item.xpath('//div[@class="p-img"]//img')[i].get('data-lazy-img'),
        #         'price': item.xpath('//div[@class="p-price"]/strong/i/text()'),
        #         'deal': item.xpath('//div[@class="p-commit"]/strong/text()'),
        #         'title': item.xpath('//div[@class="p-name"]/a/text()'),
        #         'shop': item.xpath('//div[@class="p-shop"]/span/a/text()'),
        #     }
        #     print(product)
        #     i += 1
        #     print(i)
        # else:
        #
        # print("img:", html.xpath('//div[@class="p-img"]//img')[i].get('src'))
        # print('price:',html.xpath('//div[@class="p-price"]/strong/i')[i].text)
        # print('deal:', html.xpath('//div[@class="p-commit"]/strong')[i].text)
        # print('title:' ,html.xpath('//div[@class="p-name"]/a')[i].text)
        # print('shop:', html.xpath('//div[@class="p-shop"]/span/a')[i].text)
        #
        # print(i)
    # doc = pq(html)
    # # print(doc)
    # items = doc('#J_goodsList .gl-warp .gl-item').items()
    # for item in items:
    #     product = {
    #         'img': item.find('.p-img > a > img').attr('src'),
    #         'price': item.find('.p-price').text(),
    #         'deal': item.find('.p-commit').text(),
    #         'title': item.find('.p-name').text(),
    #         'shop': item.find('.curr-shop').text(),
    #         # 'location': item.find('.location').text()
    #     }
    #     print(product)
    #     i+=1
    #     print(i)
def main():
    for page in range(2,102):
        next_page(page)
def next_page(page):
    print("正在爬取第", page, "页！！！")

    # url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E5%B0%8F%E7%B1%B3%E6%89%8B%E6%9C%BA&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest&bcoffset=1&ntoffset=7&p4ppushleft=2%2C48&data-key=s&data-value=' + str(
    #     44 * page - 1)
    # browser.get(url)
    try:
        if page > 1:
            next = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next')
            ))
            next.click()
            # sub.click()
            # try:
            #     browser.switch_to.frame('ks-component985')
            #     yanzheng = wait.until(EC.presence_of_element_located(
            #         (By.CSS_SELECTOR, '#nc_1_n1z')
            #     ))
            #     if yanzheng:
            #         # browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            #         ActionChains(browser).drag_and_drop_by_offset(yanzheng, 400, 0).perform()
            #         sub.click()
            # except:
            #     pass
        time.sleep(5)
        xinxi()
    except TimeoutException:
        next_page(page)

def save_mongo(result):
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

