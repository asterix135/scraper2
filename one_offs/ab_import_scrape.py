import pymysql
import re
from url_queue import URLSearchQueue
from base import process_external_url_queue
from bs4 import BeautifulSoup
from selenium import webdriver

HOST = 'localhost'
PASSWORD = 'python'
USER = 'python'
DB = 'cpa'
PORT = 3306


def main():
    # Instantiate stuff
    driver = webdriver.PhantomJS()
    email_set = set([])
    list_of_external_queues = []
    set_of_external_base_urls = set([])
    with open('ab_cpa.txt', 'r') as f:
        text_bulk = f.readlines()
    email_pattern = r'\S+@\S+\.\w+'
    website_pattern = r'[wW][wW][wW]\.\S+\.[\w\.]+'

    # Extract relevant info from data
    for line in text_bulk:
        match = re.findall(email_pattern, line)
        if len(match) > 0:
            for email in match:
                email_set.add(email)
        match = re.findall(website_pattern, line)
        if len(match) > 0:
            for website in match:
                if website not in set_of_external_base_urls:
                    set_of_external_base_urls.add(website)
                    list_of_external_queues.append(
                        URLSearchQueue('http://' + website)
                    )

    # add emails to database
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

    # Crawl websites for additional emails
    while len(list_of_external_queues) > 0:
        active_queue = list_of_external_queues.pop()
        process_external_url_queue(active_queue, driver)


if __name__ == '__main__':
    main()
