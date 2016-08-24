"""
Goal of this routine is to build and save a list of CPA firms
Do not follow external links
"""

from start_url_list import start_url_list
from urllib.parse import urlparse
import parse_page
import url_queue
import json
import csv
import re

# 1. Initialize queue
cpa_queue = url_queue.URLSearchQueue()

# 1a. Initialize firm_list (consider making this a MySQL d/b)
# firm_list = []
# set_of_external_url_queues = set([])
set_of_emails = set([])

# 2. Various static values
# START_URL = 'http://www.cpaontario.ca/public/apps/cafirm/sortfims.aspx?FirmRegionNumber=5&locality=A'
# START_URL = 'http://www.cpaontario.ca/public/apps/cafirm/centralont.aspx'
JAVA_PREFIX = 'http://www.cpaontario.ca/public/apps/cafirm/'
SITE_PREFIX = 'http://www.cpaontario.ca'

# 3. Add START_URL(s) to queue
# cpa_queue.enqueue(START_URL)
for url in start_url_list:
    cpa_queue.enqueue(url)


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


# 5. function to scrape base tree
def scrape_cpa_tree(queue):
    firm_list = []
    set_of_external_urls = set([])
    list_of_external_url_queues = []
    while queue.queue.len() > 0:
        curr_url = queue.dequeue()
        page_tree = parse_page.fetch_page(curr_url)
        if page_tree is not None:
            url_list = parse_page.extract_urls(page_tree)
            for url in url_list:
                # This is a link to firm details
                if url[:36] == "javascript:open_window('details.aspx":
                    queue.enqueue(JAVA_PREFIX + url[24:len(url)-2])
                # Deal with paginated lists
                elif url[:10] == 'javascript':
                    # TODO: Deal with this situation
                    pass
                # Enqueue links to same site
                elif url[:len(SITE_PREFIX)] == SITE_PREFIX:
                    queue.enqueue(url)
                # Put external links into a separate queue
                if 'details.aspx?searchnumber=' in curr_url:
                    parsed_url = urlparse(url)
                    external_base_url = \
                        '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
                    external_url_queue =url_queue.URLSearchQueue()
                    if external_base_url not in set_of_external_urls:
                        external_url_queue.enqueue(external_base_url)
                    if url != external_base_url and \
                                    url not in set_of_external_urls:
                        external_url_queue.enqueue(url)
                    if external_url_queue.queue_len() > 0:
                        list_of_external_url_queues.append(external_url_queue)
            # if curr_url is detail page, extract firm info and add to firm_list
            if 'details.aspx?searchnumber=' in curr_url:
                firm_list.append(extract_firm_info(page_tree))
    return list_of_external_url_queues, firm_list

# 5a. scrape tree
external_sites, firm_details = scrape_cpa_tree(cpa_queue)

# num_scraped = 0
# while cpa_queue.queue_len() > 0:
#     num_scraped += 1
#     # Extract URLs and add to queue
#     curr_url = cpa_queue.dequeue()
#     page_tree = parse_page.fetch_page(curr_url)
#     if page_tree is not None:
#         url_list = parse_page.extract_urls(page_tree)
#         for url in url_list:
#             if url[:36] == "javascript:open_window('details.aspx":
#                 cpa_queue.enqueue(JAVA_PREFIX + url[24:len(url)-2])
#             elif url[:10] == 'javascript':
#                 # TODO: Deal with this situation
#                 pass
#             elif url[:len(SITE_PREFIX)] == SITE_PREFIX:
#                 cpa_queue.enqueue(url)
#             else:
#                 parsed_url = urlparse(url)
#                 external_url = \
#                     '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
#                 external_url_queue = url_queue.URLSearchQueue()
#                 if external_url not in set_of_external_urls:
#                     external_url_queue.enqueue(external_url)
#                 if url != external_url and url not in set_of_external_urls:
#                     external_url_queue.enqueue(url)
#                 if external_url_queue.queue_len() > 0:
#                     set_of_external_url_queues.add(external_url_queue)
#
#         # If this is a details page, extract firm info and add to firm_list
#         if 'details.aspx?searchnumber=' in curr_url:
#             firm_list.append(extract_firm_info(page_tree))


# 6. Define routine to extract email address from text
def extract_emails(soup_item):
    """
    Extracts emails from both web page text and hrefs
    returns a set of unique emails
    :param soup_item: beautiful soup tree
    :return: set of email addresses as text
    """
    text_block = soup_item.get_text()
    email_list = re.findall(r'[\w\.-]+@[\w\.-]+', text_block)
    email_list.extend(parse_page.extract_emails(soup_item))
    return set(email_list)


# 7. Define routine to extract emails from external websites
def process_external_url_queue(queue_of_urls):
    """
    Crawls all in-domain pages and extracts email addresses
    :param queue_of_urls:
    :return:
    """
    base_url = queue_of_urls.get_base_url()
    domain_emails = set([])
    while queue_of_urls.queue_len() > 0:
        curr_url = queue_of_urls.dequeue()
        page_tree = parse_page.fetch_page(curr_url)
        if page_tree is not None:
            url_list = parse_page.extract_urls(page_tree, base_url)
            for url in url_list:
                queue_of_urls.enqueue(url)
            emails_on_page = extract_emails(page_tree)
            domain_emails.update(emails_on_page)
    return domain_emails


# 8. Go through each external URL and scrape emails
while len(external_sites) > 0:
    active_queue = external_sites.pop()
    set_of_emails.update(process_external_url_queue(active_queue))


with open('firm_list.csv', 'w') as csvfile:
    fieldnames = ['firm_details', 'firm_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for firm in firm_details:
        writer.writerow(firm)

with open('email_list.csv', 'w') as csvfile:
    fieldnames = ['email']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for email in set_of_emails:
        writer.writerow(email)
