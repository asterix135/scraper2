from base import *
from url_queue import URLSearchQueue


def process_failures():
    # 1. Initialize queue
    cpa_queue = url_queue.URLSearchQueue()

    # 1a. Initialize firm_list (consider making this a MySQL d/b)
    set_of_emails = set([])
    driver = webdriver.PhantomJS()

    # Create list of queues from failed list
    external_sites = []
    with open('failures.txt', 'r') as f:
        for line in f:
            new_url = line[9:]
            external_sites.append(URLSearchQueue(new_url))

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


if __name__ == '__main__':
    process_failures()
