#!/usr/bin/env python3
# Version: 0.1

import requests
import re
import sys
import os

"""
Notes:

"""
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

def scrape(url):
    r = requests.get(url)
    matches = re.findall(r'href=[\'|\"](\S*)[\'|\"]', r.text)
    fixed = []
    for x in matches:
        try:
            if x[0] == '/':
                fixed.append(f'{url}{x}')
                
            elif x[0:4] == 'http':
                fixed.append(x)
            
            else:
                pass
        except IndexError:
            pass

    # print(matches)
    return fixed

def robo_text(url):
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

def url_regex(url, st, end):
    # regex for pulling out different parts of the given URL
    # ex. (1)(http://www.) (2)(example.com) (3)(/index.html)
    urlobj = re.match(r'((?:https?|ftp)://(?:[a-zA-Z]+\.)?)([^/\r\n]+)(/[^\r\n]*)?', url)
    rooturl = url[urlobj.start(st):urlobj.end(end)]
    return rooturl

if __name__ == '__main__':
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
        # Init variables for main function
        # Modified below if needed
        # TODO add notes as to the use of each key
        props = {
                    'maxDepth': 2,
                    'roboAvoid': [],
                    'robots': [],
                    'rude': False,
                    'args': sys.argv[1:],
                    'root': [],
                    'pthExist': True,
                    'visited': []
                }
        
        # Remove this once converted to use above dict
        '''
        max_depth = 2
        robo_avoid = []
        robots = []
        rude = False
        args = sys.argv[1:]
        path_exists = True
        '''
        # Remove above once dict finalized

        # Look for custom max scan depth
        if '-m' in props['args']:
            props['maxDepth'] = int(props['args'][props['args'].index('-m') + 1])
            props['args'].pop(props['args'].index('-m') + 1)
            props['args'].pop(props['args'].index('-m'))
        
        # Look to see if user wants to be rude
        if '-r' in props['args']:
            props['args'].pop(props['args'].index('-r'))
            props['rude'] = True 

        else:
            props['visited'] = robo_text(props['args'][0])
            props['robots'].append(props['args'][0])

        try:
            # extract root URL ex. http://www.google.com -> google.com
            rooturl = url_regex(props['args'][0],2 ,2)
        except AttributeError:
            print('Invalid URL')
            print('Use full url such as: https://www.google.com')
            sys.exit()

        except:
            print('Exception occurred! See exception info below')
            print('Trying to extract root URL\n')
            print(sys.exc_info())
            sys.exit()

        # Create full path to users home folder and output directory
        filepath = os.path.expanduser('~/Spider_Soup/')

        # Check to see if output folder exists and create if not 
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Call main function to run recursively and spider the web page
        url_out, visited = main(args[0], max_depth, url_root = args[0], visited = robo_avoid, robots = robots, rude = rude)

        # Sort output for writing to final file
        url_out.sort()

        # Create alternate filenames if file exists already
        num = ''
        idx = 2
        while path_exists == True:
            if os.path.exists(f'{filepath}{rooturl}{num}.txt'):
                num = f'({str(idx)})'
                idx += 1

            else:
                file_out = f'{filepath}{rooturl}{num}.txt'
                path_exists = False

        # Write harvested links to file
        with open(file_out, 'a') as urltext: 
            for line in url_out:
                urltext.write(line + '\n')

        # TODO Add message telling user where final file was written when program exits