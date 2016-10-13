from bs4 import BeautifulSoup
from selenium import webdriver
import parse_page
JAVA_PREFIX = 'http://www.cpaontario.ca/public/apps/cafirm/'


def find_link_text_for_java_page(selenium_page, test_start=''):
    """
    Returns a list of link text values that match javascript link value
    """
    soup_page = BeautifulSoup(selenium_page.page_source, 'lxml')
    link_list = []
    for link in soup_page.find_all('a'):
        test_link = link.get('href')
        if test_link is not None and test_link[:len(test_start)] == test_start:
            link_list.append(link.string)
    return link_list


def extract_urls(soup_item):
    """
    We only want to extract page links to firm listings
    :param soup_item:
    :return:
    """
    link_list = []
    url_list = parse_page.extract_urls(soup_item)
    for url in url_list:
        if url[:36] == "javascript:open_window('details.aspx":
            link_list.append(JAVA_PREFIX + url[24:len(url)-2])
    return link_list


def load_javascript_page(url, prefix='javascript:', driver=None):
    """
    Finds all javascript links matching prefix.  Loads each one, parses page
    and returns list of found urls
    :param url:
    :param prefix:
    :return:
    """
    new_url_list = []
    if not driver:
        driver = webdriver.PhantomJS()
    driver.get(url)
    link_text_list = find_link_text_for_java_page(driver, prefix)
    for link_text in link_text_list:
        next_page = driver.find_element_by_link_text(link_text)
        next_page.click()
        new_page_soup = BeautifulSoup(driver.page_source, 'lxml')
        new_url_list.extend(extract_urls(new_page_soup))
        driver.back()
    return new_url_list

def fetch_page(url, driver=None):
    """
    load web page and return as Beautiful Soup object
    """
    fn_driver_created = False
    if not driver:
        driver = webdriver.PhantomJS()
        fn_driver_created = True
    if url[-3:].lower() == 'pdf':
        # print('skipping pdf: %s' % (url))
        return
    try:
        old_page_source = driver.page_source
    except Exception as exc:
        print('%s error on page %s' % (exc, url))
        return
    try:
        driver.get(url)
    except Exception as exc:
        print('%s error on page %s' % (exc, url))
        return
    if driver.page_source != old_page_source:
        tree = BeautifulSoup(driver.page_source, 'lxml')
    else:
        tree = None
    if fn_driver_created:
        driver.close()
        driver.quit()
    return tree
