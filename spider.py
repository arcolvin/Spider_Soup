#!/usr/bin/env python3
# Version: 0.1

import requests
import re
import sys

"""
Notes:

"""

class spider:
    def __init__(self):
        # TODO: Set comments to explain these
        self.final = set()
        self.working = set()
        self.maxDepth = 2
        self.roboAvoid = set()
        self.robots = []
        self.rude = False
        self.root = []
        self.pthExist = True
        self.visited = []
        

    def crawl(self):
        pass


    def scrape(self, url):
        # Get HTML
        r = requests.get(url)
        
        # Find full URLs in the HTML
        matches = set(re.findall(r'[\'\"]((?:https?|telnet|ldaps?|ftps?)\:\/\/[\w|\d|\.|\:]+\/?.*?)(?:\?.*?)?[\'\"]', r.text))
        
        # Find relative matches in HTML
        relativeMatches = set(re.findall(r'[\'\"](?:(?!https?|telnet|ldaps?|ftps?))(\/?[\w|\d|\.]+)[\'\"]', r.text))

        # Identify base URL for relative link fix
        baseUrlMatch = re.match(r'((?:https?|telnet|ldaps?|ftps?)\:\/\/[\w|\d|\.|\:]+)\/?.*?', url)
        baseURL = url[baseUrlMatch.start(1):baseUrlMatch.end(1)]

        # Make relative matches into full matches for processing
        # Add to main matches set
        for match in relativeMatches:
            if match[0] == '/':
                matches.add(baseURL + match)
                
            else:
                matches.add(baseURL + '/' + match)

        # print(matches)
        return matches


    def robo_text(self, url):
        robo_avoid = []
        # Attempt to call the URL to find robot.txt entries
        try:
            headers = { 'User-Agent' : "Mozilla/5.0" }
            req = urlreq.Request(url + '/robots.txt', None, headers)
            html = urlreq.urlopen(req)
            for line in html:
                robo_rule = ''
                robo_obj = re.match(r'[^\/]+(\/\S+)', line.decode('unicode_escape'))
                try:
                    robo_rule = line[robo_obj.start(1):robo_obj.end(1)].decode('unicode_escape')
                    robo_avoid.append(url + robo_rule)
                except AttributeError:
                    # skip blank lines or lines with no rules to match
                    continue
                except:
                    print('\nException occurred while building robo avoid list.\n')
                    print('\n', sys.exc_info(), '\n')

        # Return error if robots.txt URL is bad
        except ValueError:
            print('\nInvalid URL found while parsing robots.txt')
            print('working with: {}\n'.format(url))
            print('\n', sys.exc_info(), '\n')

        except KeyboardInterrupt:
            sys.exit()
        
        # Return generic error message if unexpected error occurs
        except:
            print('\nException occurred while reading robot.txt')
            print('working with: {}\n'.format(url))
            print('\n', sys.exc_info(), '\n')

        return robo_avoid


if __name__ == '__main__':
    print('This is intended to be imported into another script ' + \
          'and used as the heart of a scraping program.')
    print('Import this into a script and try again')
    