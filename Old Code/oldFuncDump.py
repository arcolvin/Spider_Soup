#!/usr/bin/python3

import sys
import os
import spider # Wont work, Refers to old spider
import requests
import re



def oldMain():
        # program INIT
    if len(sys.argv) < 2:
        # usage string if not enough arguments
        print(f'Usage: {sys.argv[0]} <parent url to scan>')
        print(f'Enter {sys.argv[0]} --help for more info')
        sys.exit()

    # Look for help string option
    elif '--help' in sys.argv:
        print(helpMsg(sys.argv[0]))
        sys.exit()

    else:
        # Init spider and its values
        args = sys.argv[1:],

        # Create spider class for further processing and tracking
        crawler = spider.spider

        # Look for custom max scan depth
        if '-m' in args:
            crawler.maxDepth = int(args[args.index('-m') + 1])
            args.pop(args.index('-m') + 1)
            args.pop(args.index('-m'))
        
        # Look to see if user wants to be rude
        if '-r' in args:
            args.pop(args.index('-r'))
            crawler.rude = True 

        else:
            crawler.visited = crawler.robo_text(args[0])
            crawler.robots.append(args[0])

        # Call main function to run recursively and spider the web page
        urls, visited = crawler.crawl()

        # Sort output for writing to final file
        list(urls)
        urls.sort()


def helpMsg(fn):
    help_str = f'''

    This is the help section for {fn}
    There are 2 extra options available to you:

    -m <#>          Use flag -m to change maximum scan depth.
                    Give an integer value to define max depth.
                    Recommended and default max is 2.

    -r              This flag will make the spider ignore robots.txt


    Make sure to provide the whole URL such as:

    https://www.google.com

    Beautiful Soup required to run. If using Ubuntu you can install it with:

    sudo apt install python-bs4

    A text file located within ~/Spider_Soup/ will be written with your results.
    The text file should have the domain name for the root web page scanned.

    command ex. {fn} http://www.example.com -m 2 -r
                {fn} -r http://www.example.com -m 3
                {fn} -m 4 http://www.example.com
                {fn} http://www.example.com

    Thank you for using Spider_Soup!


    '''
    return help_str

def writeOut(url_out, startURL):
    # URL out is the data structure holding all of the collected URLs
    # Start URL is the URL originally provided by the user at program start

    # Create full path to users home folder and output directory
    filepath = os.path.expanduser('~/Spider_Soup/')
    path_exists = True
    # Check to see if output folder exists and create if not 
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Create alternate filenames if file exists already
    num = ''
    idx = 2
    while path_exists == True:
        if os.path.exists(f'{filepath}{startURL}{num}.txt'):
            num = f'({str(idx)})'
            idx += 1

        else:
            file_out = f'{filepath}{startURL}{num}.txt'
            path_exists = False

    # Write harvested links to file
    with open(file_out, 'a') as urltext: 
        for line in url_out:
            urltext.write(line + '\n')

    # TODO Add message telling user where final file was written when program exits

def scrape(url):
    r = requests.get(url)
    matches = re.findall(r'href=[\'|\"](\S*)[\'|\"]', r.text)
    fixed = []
    for x in matches:
        try:
            if x[1] == '/':
                fixed.append(f'{url}{x}')
                
            elif x[1:4] == 'http':
                fixed.append(x)
            
            else:
                pass
        except IndexError:
            pass

    # print(matches)
    return fixed

res = list(set(scrape('https://dinkyouverymuch.com')))

res.sort()

with open('spiderOut.txt', 'w') as f:
    for x in res:
        f.write(x + "\n")


# old spider class
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

