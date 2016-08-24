from bs4 import BeautifulSoup
from selenium import webdriver
import parse_page
from base import JAVA_PREFIX


def find_link_text_for_java_page(selenium_page, test_start=''):
    """
    Returns a list of link text values that match javascript link value
    :param soup_item:
    :return:
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


def load_javascript_page(url, prefix='javascript:'):
    """
    Finds all javascript links matching prefix.  Loads each one, parses page
    and returns list of found urls
    :param url:
    :param prefix:
    :return:
    """
    new_url_list = []
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
