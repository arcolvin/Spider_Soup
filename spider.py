#!/usr/bin/env python3
# Version 1.1
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

'''
This allows for logs to work even if class is imported
all log events in this script should be called as
log.LEVEL('Log Message')
'''
log = logging.getLogger(__name__)

class spider():

    def __init__(self):
        '''
        Provide initial variables for scraping use
        '''

        # Active HTML object
        self.html = None
        # URL Processing Queue
        self.queue = set()
        # URL Processing Queue for next level
        self.nextqueue = set()
        # Processed URL list (for final Export)
        self.visited = set()
        # Robots.txt deny regex string set
        self.deny = set()
        # Robots.txt allow set
        self.allow = set()
        # For tracking visited robots.txt pages
        self.roboVisited = set ()
        # current depth
        self.depth = 0
        # Max Depth
        self.maxdepth = 2
        # base URL for active HTML Object
        self.baseURL = ''
            # For robots.txt tracking
            # Also for relative link build out
        self.currentURL = ''
        # Toggle for polite or rude spider (used in self.nextURL())
        self.polite = True

        log.debug('Spider initialized')
        log.debug('Initial variable values:')
        log.debug(f'html: {self.html}')
        log.debug(f'queue: {self.queue}')
        log.debug(f'next queue: {self.nextqueue}')
        log.debug(f'visited: {self.visited}')
        log.debug(f'deny: {self.deny}')
        log.debug(f'allow: {self.allow}')
        log.debug(f'roboVisited: {self.roboVisited}')
        log.debug(f'depth: {self.depth}')
        log.debug(f'maxdepth: {self.maxdepth}')
        log.debug(f'baseURL: {self.baseURL}')
        log.debug(f'currentURL: {self.currentURL}')


    def crawl(self):
        '''
        process for navigating to and collecting new HTML object
        should stop if maximum depth reached
        should save HTML object to self.currentURL
        '''
        
        if self.depth >= self.maxdepth:
            return None

        else:
            log.info(f'Requesting HTML for: {self.currentURL}')
            
            self.html = requests.get(self.currentURL)

            log.debug('HTML collected with http status code' + \
                    f' of {self.html.status_code}')
            log.debug(f'Apparent encoding: {self.html.apparent_encoding}')

            return None


    def scrape(self):
        '''
        Process for reading and extracting data from HTML object
        '''
        # TODO Allow user to provide custom REGEX for custom data extraction
        
        if self.depth >= self.maxdepth:
            return None

        else:
            # Identify base URL of current processed URL            
            self.baseURL = self.base(self.currentURL)
            log.debug(f'BaseURL identified: {self.baseURL}')

            # Collect lists of all found full and relative URLS
            fullURLs = self.full(self.html.text)
            relativeURLs = self.rel(self.html.text)
            
            # Process these lists and save values to queue
            log.info("Adding found URL's to next queue")
            for x in fullURLs:
                self.nextqueue.add(x)

            for x in relativeURLs:
                self.nextqueue.add(self.baseURL + x.lstrip('/'))

            log.info('Next queue updated')

            log.debug(f'Current Queue: {self.queue}')
            log.debug(f'Next Queue: {self.nextqueue}')
            log.debug(f'Queue Length: {len(self.queue)}')
            log.debug(f'Next Queue Length: {len(self.nextqueue)}')
            log.debug(f'Current Depth: {self.depth}')
            log.debug(f'Max Depth: {self.maxdepth}')

            return None
    

    def nextURL(self):
        '''
        self.nextURL() will identify next URL in the queue and prep variables
        for next loop. If needed this block will also increment current scan
        depth so we can eventually stop the program
        '''

        if self.queue == set():
            # Promote to next level when primary queue is empty
            self.queue = self.nextqueue
            self.nextqueue = set()
            self.depth += 1

        try:
            # Save current URL to visited list
            self.visited.add(self.currentURL)

            # Remove visited URLs from current queue to avoid duplicate visits
            self.queue -= self.visited

            # Remove robots.txt values for polite spiders
            if self.polite:
                self.robot()

            # prepare next URL for processing
            self.currentURL = self.queue.pop()

        except KeyError:
            log.info('Queue was empty when trying to increment. ' + \
                      'Reporting findings and stopping spider')
            log.debug(f'Found URLs: {self.visited}')
            self.currentURL = None

            # This can be used to stop a loop of there is no more to process
            return False

        # This can be used to continue a loop of there is more to process
        return True


    def base(self, url):
        '''
        Method to find the base URL from a provided URL string
        expects a string returns a string
        '''
        # REGEX for base URL
        base_R = r'((?:https?|telnet|ldaps?|ftps?)\:\/\/[\w|\d|\.|\:]+)\/?.*?' 

        # rstrip a slash if it exists, then add one in
        # guarantees there is exactly one / on the base url for concatenation
        # with a relative url path
        return re.search(base_R , url).group().rstrip('/') + '/'


    def full(self, html):
        '''
        Method to find all of the full URLs from a provided html text
        Expects html text passed via argument
        returns a list of strings
        '''
        full_R = r'href=[\'\"]((?:https?|telnet|ldaps?|ftps?)' +\
                 r'\:\/\/[\w|\d|\.|\:]+\/?.*?)[\'\"]'

        # Collect lists of all found full and relative URLS
        return re.findall(full_R, html)


    def rel(self, html):
        '''
        Method to find all of the URLs from a provided html text
        Expects html text passed via argument
        returns a list of strings
        '''
        # REGEX for relative URLs
        rel_R = r'href=[\'\"](?:(?!https?|telnet|ldaps?|ftps?))' +\
                r'(\/?[\w|\d|\.]+)[\'\"]'
        
        return re.findall(rel_R, html)


    def robot(self, queue=None):
        '''
        Process to call in and remove robots.txt values from processing queue
        With Auto this will look at all URLs in the current queue during the
        cleanup phase of the next URL function

        Expects an iterable set of URLs
        saves found robots exclusions to self.allow and self.deny
        also curates the queue to eliminate denied paths
        '''
        # NOTE: Maybe put all queue base URLs in a temporary set to ensure
        #       we don't visit a given txt twice 

        # TODO: Add Sitemap and user agent compatibility
        # Initialize queue if no parameter provided
        if queue == None:
            queue = self.queue

        # Find base URL for element at hand
        for url in queue:
            if self.base(url) in self.roboVisited:
                continue

            else:
                base = self.base(url)

                log.info(f'Requesting robots.txt for: {base}')
                
                # Request the robots.txt of the base URL
                roboHTML = requests.get(f'{base}robots.txt')
                self.roboVisited.add(base)
                    
                log.debug('robots.txt collected with http status code' + \
                        f' of {roboHTML.status_code}')
                log.debug(f'Apparent encoding: {roboHTML.apparent_encoding}')

                # Create new sets for processing
                # This allows for better debugging messages
                allow = set()
                deny = set()

                # Escape regex Chars that might show up in the URL
                # Prepare the found line as a regex string for later matching
                mkReg = lambda x: x.replace('.', '\.')\
                    .replace('?', '\?')\
                    .replace('+', '\+')\
                    .replace('$', '\$')\
                    .replace('^', '\^')\
                    .replace('&', '\&')\
                    .replace('-', '\-')\
                    .replace('|', '\|')\
                    .replace('(', '\(')\
                    .replace(')', '\)')\
                    .replace('[', '\[')\
                    .replace(']', '\]')\
                    .replace('*', '.*')

                # Parse robots.txt looking for allow and deny values
                for line in roboHTML.text.split('\n'):
                    try:
                        rule, path = line.split()
                    except ValueError:
                        log.debug('Empty Line in robots.txt')
                    path = path.lstrip('/')
                    if rule.upper() == 'ALLOW:':
                        log.debug(f'Found Allow Match: {line}')
                        allow.add(f'({mkReg(base + path)})')

                    elif rule.upper() == 'DISALLOW:':
                        log.debug(f'Found Disallow Match: {line}')
                        deny.add(f'({mkReg(base + path)})')

                    else:
                        log.debug(f'Robots line not matched: {line}')

                log.debug(f'Robots.txt parsed for {base}')
                log.debug(f'Robots.txt allow set for {base}: {allow}')
                log.debug(f'Robots.txt deny set for {base}: {deny}')
                
                # Add all newly found entries to existing allow / deny sets
                self.allow.update(allow)
                self.deny.update(deny)

        # Create a static set to iterate over since self.queue will likely
        # change during this block of code
        safeQueue = self.queue.copy()

        # NOTE: Robots Attempt 1
        '''
        # This is broken, It does not block removing an approved URL
        for regex in self.allow:
            for url in safeQueue:
                if re.match(regex, url):
                    log.debug(f'Found robot.txt permitted URL in queue: {url}')
                    continue 

        for regex in self.deny:
            for url in safeQueue:
                self.queue.remove(url)
                log.debug('found and removed robots.txt banned URL in' +\
                         f' queue: {url}')
        '''
        # NOTE: Robots Attempt 2 (sorta works)
        '''
        # NOTE: This is allowing URLs through that should be blocked
        # The ANY() function does not show what is matching so this will likely
        # need to be reworked somehow so the regex can be better examined
        for url in safeQueue:
            if any(re.search(regex, url) for regex in self.allow):
                log.debug(f'Found robot.txt permitted URL in queue: {url}')
                continue 

            elif any(re.search(regex, url) for regex in self.deny):
                self.queue.remove(url)
                log.debug('found and removed robots.txt banned URL in' +\
                         f' queue: {url}')
        '''
        # NOTE: I think this is all dumb. I probably need to drop this into a function
        # to keep it readable which is what i am trying to accomplish here so we
        # dont end up with 7 layers of indentation

        # NOTE: Robots attempt 3
        # Maybe try for a intersection of two sets? if len intersection 0 no match?
        for url in safeQueue:
            if len: # TODO: Build logic to check wether the URL exists in two sets
                log.debug(f'Found robot.txt permitted URL in queue: {url}')
                continue 

            elif any(re.search(regex, url) for regex in self.deny):
                self.queue.remove(url)
                log.debug('found and removed robots.txt banned URL in' +\
                         f' queue: {url}')

        log.info(f'Finished robots.txt cleanup for layer {self.depth}')

        return None


    def report(self):
        '''
        Method to do final export of collected data
        '''
        '''
        TODO: Make this name the file based on current time to avoid clobber.
        If continuous reporting is needed, might need to create file at
        beginning track filename and reuse as many times as needed until program
        completion
        '''
        with open('spiderURLs.txt', 'w') as f:
            for x in sorted(list(self.visited)):
                f.write(x + '\n')
        
        return None


    def auto(self, startURL, max_depth=None):
        '''
        This block will automate the scraping process for an end user if
        desired, but a user can also use other methods in this class to 
        manually scrape or read html objects

        Expects user to provide a starting URL and depth

        Default depth is 2 layers but can be set to any integer value
        '''
        self.currentURL = startURL

        if max_depth != None:
            # This allows the default value of 2 to be overridden if assigned
            # Otherwise maxdepth will be 2
            self.maxdepth = max_depth

        again = True

        try:
            while again:
                self.crawl()
                self.scrape()
                again = self.nextURL()

        except KeyboardInterrupt:
            log.info('Keyboard Interrupt. ' + \
                     'Stopping Spider and reporting findings')
            self.visited.update(self.queue)
            self.visited.update(self.nextqueue)

        finally:
            self.report()

        return None


if __name__ == '__main__':
    # Driver code for local testing
    '''
    Should be implemented into another script to match required processes
    for the specified use case

    Default auto action is to do 2 layers of scraping for testing
    '''
    
    # Log to terminal for testing
    logging.basicConfig(level='DEBUG')

    # Hardcode starting URL for testing
    startURL = 'https://yahoo.com'

    # Spider instance for testing
    s = spider()

    ########################
    # Test Use Cases Below #
    ########################

    ###############################
    # for auto config and testing #
    ###############################

    # s.auto(startURL) # Valid Parameters for auto(): (Start URL, Max Depth)


    #######################
    # Robots text testing #
    #######################
    # TODO: below google URL should be blocked but is showing as allowed
    s.queue = set([startURL] + ['https://google.com/?hl=132&asdfaf&gws_rd=ssl'])
    s.robot()