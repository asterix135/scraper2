from urllib.parse import urlparse
import url_queue
import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver


HOST = 'localhost'
PASSWORD = 'python'
USER = 'python'
DB = 'cpa'
PORT = 3306


def main():
    # 1. instantiate stuff
    canada_queue = url_queue.URLSearchQueue()
    list_of_external_queues = []
    set_of_external_base_urls = set([])
    email_set = set([])
    list_of_firms = []
    driver = webdriver.PhantomJS()
    url = 'https://www.cpacanada.ca/en/the-cpa-profession/cpas-and-what-we-do/find-an-accounting-firm'
    url_start = '/en/the-cpa-profession/cpas-and-what-we-do/find-an-accounting-firm'

    # 2. get internal firm links from base page
    driver.get(url)
    tree = BeautifulSoup(driver.page_source, 'lxml')
    for url in extract_firm_page_urls(tree, url_start):
        canada_queue.enqueue(url)

    # 3. grab relevant info from each individual firm listing
    n = 0
    while canada_queue.queue_len() > 0:
        n += 1
        if n % 100 == 0:
            print('processed %s cpacanada pages' % n)

        curr_url = canada_queue.dequeue()
        firm_name, firm_details, email_list, web_list = scrape_for_firm_info(
            curr_url, driver
        )
        if len(web_list) > 0:
            for site in web_list:
                if site is not None and 'linkedin' not in site \
                        and 'facebook' not in site:
                    if site[:4] != 'http':
                        site = 'http://' + site
                    update_external_queue(list_of_external_queues,
                                          set_of_external_base_urls,
                                          site)
        if len(email_list) > 0:
            email_set.update(email_list)
        list_of_firms.append({'firm_name': firm_name,
                              'firm_details': firm_details})

    connection = pymysql.connect(host=HOST,
                                 password=PASSWORD,
                                 port=PORT,
                                 user=USER,
                                 db=DB)

    sql = 'INSERT INTO emails VALUES (%s)'
    with connection.cursor() as cursor:
        for email in email_set:
            try:
                cursor.execute(sql, email)
            except Exception as exc:
                print('Error: %s \nfailed to write %s' % (exc, email))

    connection.commit()


def update_external_queue(list_of_queues, set_of_urls, new_url):
    parsed_url = urlparse(new_url)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    new_queue = url_queue.URLSearchQueue()
    if base_url not in set_of_urls:
        new_queue.enqueue(base_url)
        set_of_urls.add(base_url)
        if new_url != base_url:
            new_queue.enqueue(new_url)
            set_of_urls.add(new_url)
    list_of_queues.append(new_queue)


def scrape_for_firm_info(url, driver=None):
    """
    Extracts firm name, detail text, any emails and web site from page
    :param url:
    :param driver:
    :return:
    """
    driver_created = False
    if not driver:
        driver = webdriver.PhantomJS()
        driver_created = True
    driver.get(url)
    firm_elements = driver.find_elements_by_id(
        'lockedcontent_0_leftcolumn_0_pnlFirmNames'
    )
    if len(firm_elements) > 0:
        firm_name = firm_elements[0].text
    else:
        firm_name = ''

    email_elements = driver.find_elements_by_id(
        'lockedcontent_0_leftcolumn_0_lEmailValue'
    )
    email_list = []
    if len(email_elements) > 0:
        for element in email_elements:
            email_list.append(element.text)

    web_elements = driver.find_elements_by_id(
        'lockedcontent_0_leftcolumn_0_lWebsiteValue'
    )
    web_list = []
    if len(web_elements) > 0:
        for element in web_elements:
            web_list.append(element.text)

    firm_elements = driver.find_elements_by_id(
        'lockedcontent_0_leftcolumn_0_pnlEnhancedLayout'
    )
    if len(firm_elements) > 0:
        firm_details = firm_elements[0].text
    else:
        firm_details = ''

    return firm_name, firm_details, email_list, web_list


def extract_firm_page_urls(soup_item, test_start=''):
    link_list = []
    for link in soup_item.find_all('a'):
        test_link = link.get('href')
        if test_link is not None and test_link[:len(test_start)] == test_start:
            link_list.append('https://www.cpacanada.ca' + test_link)
    return link_list

if __name__ == '__main__':
    main()
