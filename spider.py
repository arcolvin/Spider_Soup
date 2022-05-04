#!/usr/bin/env python3
# Version 0.1
'''
This web spider will crawl the WWW and collect data as needed.

Its baseline behavior is to collect URL's with a given recursive depth
and save this to a local file.

Future versions will grant an option for a user to provide a custom
REGEX string to collect additional data.
'''

import logging
import requests
import re

# This allows for logs to work even if class is imported
# all log events in this script should be called as
# log.LEVEL('Log Message')
log = logging.getLogger(__name__)

class spider():
    def __init__(self):
        # Provide initial variables for scraping use
        
        # Active HTML object
        self.html = None
        # URL Processing Queue
        self.queue = set()
        # Processed URL list (for final Export)
        self.visited = set()
        # current depth
        self.depth = 0
        # Max Depth
        self.maxdepth = 2
        # base URL for active HTML Object
        self.baseURL = ''
            # For robots.txt tracking
            # Also for relative link buildout
        self.currentURL = ''

        log.debug('Spider initialized')
        log.debug('Initial variable values:')
        log.debug(f'html: {self.html}')
        log.debug(f'queue: {self.queue}')
        log.debug(f'visited: {self.visited}')
        log.debug(f'depth: {self.depth}')
        log.debug(f'maxdepth: {self.maxdepth}')
        log.debug(f'baseURL: {self.baseURL}')
        log.debug(f'currentURL: {self.currentURL}')

    def crawl(self, url):
        # process for navigating to and collecting new HTML object
        # should stop if maximum depth reached
        # should save HTML object to class
        
        # Extract base URL for relative URL rebuilding
        #self.baseURL = re.

        log.info(f'Requesting HTML for: {url}')
        
        self.html = requests.get(url)

        log.debug('HTML collected with http status code' + \
                  f' of {self.html.status_code}')
        log.debug(f'Apparent encoding: {self.html.apparent_encoding}')

        return None

    def scrape(self):
        # Process for reading and extracting data from HTML object
        # TODO Allow user to provide custom REGEX for custom data extraction
        


        matches = re.findall(r'href=[\'|\"](\S*)[\'|\"]', self.html.text)
        for x in matches:
            try:
                if x[1] == '/':
                    self.queue.add(f'{self.baseURL}{x}')
                    
                elif x[1:4] == 'http':
                    self.queue.add(x)
                
                else:
                    pass
            except IndexError:
                pass

        return None

    def robot(self):
        # process to call in and remove robots.txt values from processing queue
        pass

    def report(self):
        # Method to do final export of collected data
        pass

if __name__ == '__main__':
    # Driver code for local testing
    '''
    Should be implimented into another script to match required processes
    for the specified use case

    Default action is to do 2 layers of scraping for testing
    '''
    
    # Log to terminal for testing
    logging.basicConfig(level='DEBUG')

    # Hardcode starting URL for testing
    startURL = 'https://google.com'

    # Spider instance for testing
    s = spider()

    # TODO: Eventually this will need to be wrapped in a while loop
    # so that it can continue processing until we identify an exit point
    s.crawl(startURL)