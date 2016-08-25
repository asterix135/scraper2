"""
Functions to parse web page
"""
import requests  # for importing web pages
import bs4  # beautifulsoup4 - for parsing
from urllib.parse import urlparse
# from collections import deque
# import lxml  # to support bs4 - not sure if needed
# from lxml import html  # option 2 for parsing


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)
    return base_url


def fetch_page(url):
    """
    load web page and return as Beautiful Soup object
    """
    if url[-3:].lower() == 'pdf':
        print('skipping pdf: %s' % (url))
    try:
        page = requests.get(url)
    except Exception as exc:
        print('%s error on page %s' % (exc, url))
        return
    try:
        page.raise_for_status()
    # TODO: There's a non-deprecated way to do this
    except Exception as exc:
        print('There was a problem on page %s: %s' % (url, exc))
        return
    # tree1 = html.fromstring(page.text)
    tree = bs4.BeautifulSoup(page.text, 'lxml')
    return tree


def extract_urls(soup_item, test_start = ''):
    """
    extract list of all URLs from Beautiful Soup object
    optionally tests to see if start of url matches a pattern
    return list
    """
    link_list = []
    for link in soup_item.find_all('a'):
        test_link = link.get('href')
        if test_link is not None:
            if get_base_url(test_link) == '://' and len(test_link) > 0:
                if test_link[0] == '/':
                    link_list.append(test_start + test_link)
                else:
                    link_list.append(test_start + '/' + test_link)
            elif test_link[:len(test_start)] == test_start:
                link_list.append(test_link)
    return link_list


def extract_emails(soup_item):
    """
    Extract & return list of all email hrefs from Beautiful Soup object
    """
    email_list = []
    for link in soup_item.find_all('a'):
        if link.get('href') and 'mailto' in link.get('href'):
            email = link.get('href').replace('mailto:', '')
            email_list.append(email)
    return email_list


def append_to_url(url_list, start_string):
    """
    Takes a list of partial URLs and appends them to a constant start
    returns list of new URLs
    """
    new_list = []
    for url in url_list:
        new_list.append(start_string + url)
    return new_list


def enqueue_urls(url_list, queue):
    """
    checks links to see if visited
    enqueues unvisited links
    """
    for url in url_list:
        if not queue.check_visited(url):
            queue.enqueue(url)


def extract_person_info(soup_item):
    """
    extract contact information from web page
    """
    # TODO: Decide if this can be generalized - now is AB-specific
    extract = []
    for tag in soup_item.find_all('tr', {'class': 'trow_odd_b'}):
        extract.append(tag)
    return extract


def save_person_database(something):
    """
    either save entire person database
    OR append current info to database
    """