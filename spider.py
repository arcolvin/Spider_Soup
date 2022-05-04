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

# This allows for logs to work even if class is imported
# all log events in this script should be called as
# log.LEVEL('Log Message')
log = logging.getLogger(__name__)

class spider():
    def __init__(self):
        # Provide initial variables for scraping use
        
        # Active HTML object
        # URL Processing Queue
        # Processed URL list (for final Export)
        # current depth
        # Max Depth
        # base URL for active HTML Object
            # For robots.txt tracking
            # Also for relative link buildout
        pass

    def crawl(self):
        # process for navigating to and collecting new HTML object
        # should stop if maximum depth reached
        pass

    def scrape(self):
        # Process for reading and extracting data from HTML object
        # TODO Allow user to provide custom REGEX for custom data extraction
        pass

    def robot(self):
        # process to call in and remove robots.txt values from processing queue
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
