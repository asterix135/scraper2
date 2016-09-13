from base import process_external_url_queue
from url_queue import URLSearchQueue

external_queue = URLSearchQueue()
external_queue.enqueue('http://www.infonex.ca')
email_list = process_external_url_queue(external_queue)
for email in email_list:
    print(email)