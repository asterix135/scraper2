"""
Manage a Queue of URLs
Also keep track of visited URLs
"""
from collections import deque
from urllib.parse import urlparse


class URLSearchQueue:
    """
    Queue to manage URLs to be visited
    manages list of visited websites
    """

    def __init__(self, initial_value=None):
        """
        sets up Queue object with empty queue
        and empty visited list
        """
        self._search_queue = deque()
        self._visited_list = set([])
        if initial_value:
            self.enqueue(initial_value)

    def __repr__(self):
        """
        returns easy-to visualize version of queue
        """
        representation = "Queue: "
        for item in self._search_queue:
            representation += str(item) + '\t'
        representation += '\nVisited: '
        for item in self._visited_list:
            representation += str(item) + '\t'
        return representation

    def check_visited(self, url):
        """
        checks if supplied URL has been visited
        returns Boolean
        """
        return url in self._visited_list

    def url_in_queue(self, url):
        """
        Checks if supplied URL is already in queue
        return Boolean
        """
        return url in self._search_queue

    def enqueue(self, url):
        """
        enqueues supplied url
        checks to make sure not visited
        checks to make sure not in current queue
        """
        if url is not None:
            if not self.check_visited(url):
                if not self.url_in_queue(url):
                    self._search_queue.append(url)

    def dequeue(self):
        """
        dequeues and returns url from queue
        checks if url is in visited list
        if url is in visited list - pulls another one until queue is empty
        """
        if len(self._search_queue) > 0:
            test_url = self._search_queue.popleft()
            if not self.check_visited(test_url):
                self.add_to_visited(test_url)
                return test_url
            else:
                return self.dequeue()

    def add_to_visited(self, url):
        """
        adds supplied url to visited list
        """
        self._visited_list.add(url)

    def clear_visited_list(self):
        """
        clears visited list of all value
        """
        self._visited_list = set([])

    def queue_len(self):
        """
        Returns length of queue
        """
        return len(self._search_queue)

    def get_base_url(self):
        """
        returns base url of first element in queue
        :return: either string or None
        """
        if len(self._search_queue) > 0:
            first_url = self._search_queue[0]
            parsed_url = urlparse(first_url)
            return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
        else:
            return
