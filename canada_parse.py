from start_url_list import start_url_list
from urllib.parse import urlparse
import java_page_scraper
import parse_page
import url_queue
import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver

def main():
    driver = webdriver.PhantomJS()
    url = 'https://www.cpacanada.ca/en/the-cpa-profession/cpas-and-what-we-do/find-an-accounting-firm'
    driver.get(url)
    tree = BeautifulSoup(driver.page_source, 'lxml')

