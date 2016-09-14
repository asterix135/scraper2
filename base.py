"""
Goal of this routine is to build and save a list of CPA firms
Do not follow external links
"""

from start_url_list import start_url_list
from urllib.parse import urlparse
import java_page_scraper
import parse_page
import url_queue
import csv
import re
import pymysql
from selenium import webdriver
import time


# 2. Various static values
JAVA_PREFIX = 'http://www.cpaontario.ca/public/apps/cafirm/'
SITE_PREFIX = 'http://www.cpaontario.ca'
HOST = 'localhost'
PASSWORD = 'python'
USER = 'python'
DB = 'cpa'
PORT = 3306


def base():
    # 1. Initialize queue
    cpa_queue = url_queue.URLSearchQueue()

    # 1a. Initialize firm_list (consider making this a MySQL d/b)
    set_of_emails = set([])
    driver = webdriver.PhantomJS()

    # 3. Add START_URL(s) to queue
    for start_url in start_url_list:
        cpa_queue.enqueue(start_url)
    # 5b. scrape tree
    external_sites, list_of_firms = scrape_cpa_tree(cpa_queue, driver)

    with open('firm_list.csv', 'w') as csvfile:
        fieldnames = ['firm_details', 'firm_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for firm in list_of_firms:
            writer.writerow(firm)

    # 8. Go through each external URL and scrape emails
    while len(external_sites) > 0:
        active_queue = external_sites.pop()
        set_of_emails.update(process_external_url_queue(active_queue, driver))

    with open('email_list.csv', 'w') as csvfile:
        fieldnames = ['email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for email in set_of_emails:
            try:
                writer.writerow(email)
            except Exception as exc:
                print('failed to write email %s' % email)

# 4. Define routine to extract relevant information from firm pages
def extract_firm_info(soup_item):
    """
    extract from information from web page
    returns dict
    """
    firm_details = soup_item.get_text().strip()[20:].strip()[20:].strip()
    if soup_item.a is not None:
        firm_url = soup_item.a.get('href')
    else:
        firm_url = None
    return {'firm_details': firm_details, 'firm_url': firm_url}


# 5a. function to scrape base tree
def scrape_cpa_tree(queue, driver=None):
    firm_list = []
    set_of_external_urls = set([])
    list_of_external_url_queues = []
    n = 0
    while queue.queue_len() > 0:
        curr_url = queue.dequeue()
        n += 1
        if n % 100 == 0:
            print('%s base site pages scraped' % n)
        page_tree = parse_page.fetch_page(curr_url)
        if page_tree is not None:
            java_crawled = False
            url_list = parse_page.extract_urls(page_tree)
            for url in url_list:
                # This is a link to firm details
                if url[:36] == "javascript:open_window('details.aspx":
                    queue.enqueue(JAVA_PREFIX + url[24:len(url)-2])
                # Deal with paginated lists
                elif url[:23] == 'javascript:__doPostBack' and not java_crawled:
                    java_crawled = True
                    java_urls = java_page_scraper.load_javascript_page(
                        curr_url, 'javascript:__doPostBack', driver)
                    for new_url in java_urls:
                        queue.enqueue(new_url)
                # Enqueue links to same site
                elif url[:len(SITE_PREFIX)] == SITE_PREFIX:
                    queue.enqueue(url)
                # Put external links into a separate queue
                if 'details.aspx?searchnumber=' in curr_url:
                    parsed_url = urlparse(url)
                    external_base_url = \
                        '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
                    external_url_queue = url_queue.URLSearchQueue()
                    if external_base_url not in set_of_external_urls:
                        external_url_queue.enqueue(external_base_url)
                        set_of_external_urls.add(external_base_url)
                    if url != external_base_url and \
                            url not in set_of_external_urls:
                        external_url_queue.enqueue(url)
                        set_of_external_urls.add(url)
                    if external_url_queue.queue_len() > 0:
                        list_of_external_url_queues.append(external_url_queue)
            # if curr_url is detail page, extract firm info and add to firm_list
            if 'details.aspx?searchnumber=' in curr_url:
                firm_list.append(extract_firm_info(page_tree))
    return list_of_external_url_queues, firm_list


def extract_emails(soup_item):
    """
    Extracts emails from both web page text and hrefs
    returns a set of unique emails
    :param soup_item: beautiful soup tree
    :return: set of email addresses as text
    """
    text_block = soup_item.get_text()
    email_list = re.findall(r'[\w.-]+@[\w-]+\.[\w.-]+', text_block)
    email_list.extend(parse_page.extract_emails(soup_item))
    return set(email_list)


# 7. Define routine to extract emails from external websites
def process_external_url_queue(queue_of_urls, driver=None):
    """
    Crawls all in-domain pages and extracts email addresses
    :param queue_of_urls:
    :return:
    """
    driver_created = False
    if not driver:
        driver = webdriver.PhantomJS()
        driver_created = True
    base_url = queue_of_urls.get_base_url()
    connection = pymysql.connect(host=HOST,
                                 password=PASSWORD,
                                 port=PORT,
                                 user=USER,
                                 db=DB)
    print('crawling %s' % base_url)
    domain_emails = set([])
    n = 0
    while queue_of_urls.queue_len() > 0:
        curr_url = queue_of_urls.dequeue()
        n += 1
        if n % 50 == 0:
            print('%s: %s pages crawled for %s' % (time.time(), n, base_url))
        if n > 5000:
            break
        # page_tree = parse_page.fetch_page(curr_url)
        page_tree = java_page_scraper.fetch_page(curr_url, driver)
        if page_tree is not None:
            url_list = parse_page.extract_urls(page_tree, base_url)
            for url in url_list:
                queue_of_urls.enqueue(url)
            emails_on_page = extract_emails(page_tree)
            domain_emails.update(emails_on_page)
    if driver_created:
        driver.close()
        driver.quit()
    sql = 'INSERT INTO emails VALUES (%s)'
    with connection.cursor() as cursor:
        for email in domain_emails:
            try:
                cursor.execute(sql, email)
            except:
                print('failed to write %s' % email)
    connection.commit()
    return domain_emails


if __name__ == '__main__':
    base()
