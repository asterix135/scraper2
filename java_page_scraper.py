from bs4 import BeautifulSoup
from selenium import webdriver


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


def load_javascript_page(url, prefix='javascript:'):
    driver = webdriver.PhantomJS()
    driver.get(url)
    link_text_list = find_link_text_for_java_page(driver, prefix)
    for link_text in link_text_list:
        next_page = driver.find_element_by_link_text(link_text)
        next_page.click()



