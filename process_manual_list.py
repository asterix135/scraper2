"""
sets up and executes web scraper queues for manually-generated list of urls
command line arguments:
1: import file name
"""

import sys
import url_queue
from selenium import webdriver
from base import process_external_url_queue

FILENAME = 'CPA_firm_url_list.txt'


def create_site_set(filename):
    url_set = set([])
    with open(filename) as f:
        for line in f.readlines():
            url_set.add('http://' + line.strip())
    return url_set


def main(argv):
    driver = webdriver.PhantomJS()
    file_name = argv[1] if len(argv) > 1 else FILENAME
    url_set = create_site_set(file_name)
    total_urls = len(url_set)
    print('======================\nTotal urls to crawl: %s'
          '\n=======================' % str(total_urls))
    url_queue_list = []
    for url in url_set:
        url_queue_list.append(url_queue.URLSearchQueue(url))
    n = 0
    for queue in url_queue_list:
        n += 1
        process_external_url_queue(queue, driver)
        if n % 100 == 0:
            print('\n%s urls to go!\n' % str(total_urls - n))


if __name__ == '__main__':
    main(sys.argv)
