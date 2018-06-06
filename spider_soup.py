#!/usr/bin/env python3

import urllib.request as urlreq
from bs4 import BeautifulSoup
import sys, re, os, codecs

"""
Known Bugs:

    Polite spider does not respect extended robots.txt links
        ex. if '/private.php' in robots.txt will respect
        http://www.example.com/private.php
        but will not respect
        http://www.example.com/private.php/?do=newpm&u=1044475
        or similar web addresses

        We place any robots.txt exclusions into a visited list and refer
        statically to those list items. Maybe use regex to dynamically 
        look at the robotxt exclusions. This could also help with robo 
        entries such as '/clientscript/*.css' where there are dynamic links
        permitted or denied

Planned Code imporovements:
    Contain the passed variables inside a dictionary

    Make the error handling better.

    Split main function into more functions.

    Set the program to be threaded.
        limit maximum number of threads.

    look into argparse

"""

help_str = '''

This is the help section for {}
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

command ex. {} http://www.example.com -m 2 -r
            {} -r http://www.example.com -m 3
            {} -m 4 http://www.example.com
            {} http://www.example.com

Thank you for using Spider_Soup!


'''.format(sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])

# set many default values
# most if not all should be overwritten as the program runs
def main(url, max_depth, depth = 0, url_root = '', url_buff = [], visited = [], robots = [], rude = False):

    # reinit all variables for each recursion
    link_list = []
    link_list_preprocess = []
    link_list_ultimate = []
    link_list_final = []
    visit = []
    html_soup = ''
    if depth <= max_depth and url not in visited:
        # this may be the problem with chaining deeper
        # or with reaching the hidden test page in rude mode
        visited.append(url)

        # attempt to call the user given URL to look for links
        try:
            headers = { 'User-Agent' : "Mozilla/5.0" }
            req = urlreq.Request(url, None, headers)
            html = urlreq.urlopen(req).read()

        # Return user friendly error if web address is no good
        except ValueError:
            print('\nInvalid URL found while building html doc')
            print('Working with {}\n'.format(url))

        # permit the user to end the program with ctrl + c
        except KeyboardInterrupt:
            sys.exit()
        
        # Return generic error message if unexpected error occurs
        except:
            print('\nException occurred while trying to build HTML doc')
            print('Working with {}\n'.format(url))
            print('\n', sys.exc_info(), '\n')
            return [], visited

        # Parse HTML code into workable document
        html_soup = BeautifulSoup(html, 'html.parser')

        # find all links in HTML doc
        for link in html_soup.find_all('a'):
            link_list.append(link.get('href'))

        # assemble links into http(s):// form
        # discard unusable links
        for link in link_list:
            try:
                # look for relative links ex. /index.html
                if link[0] == '/' and len(link) > 1:
                    if (url_root + link) not in link_list_final and (url_root + link) not in visited:
                        link_list_final.append(url_root + link)

                # if given a full link process it here ex. http://www.example.com
                elif link[0:4].upper() == 'HTTP' or link[0:3].upper() == 'FTP':
                    if link not in link_list_final and link not in visited:
                        link_list_final.append(link)

                        # If given absolute URL, respect robots.txt
                        if url_root not in robots and rude == False:
                            robo_avoid = robo_text(link)
                            for itm in robo_avoid:
                                if itm not in visited:
                                    visited.append(itm)
                            robots.append(url_regex(link, 1, 2))

                # Ignore root links ex. /
                elif link[0] == '/' and len(link) == 1:
                    continue

                # look for relative links not starting in "/" ex. index.php
                else:
                    if (url_root + '/' + link) not in link_list_final and (url_root + '/' + link) not in visited:
                        link_list_final.append(url_root + '/' + link)

            except TypeError:
                # go to next link in loop if error occurs
                continue

            except KeyboardInterrupt:
                # let user exit program with ctrl + c
                sys.exit()

            except:
                # throw out seemingly invalid links
                print('\nException occurred while building link list\n')
                print('working with: {}\n'.format(link))
                print('\n', sys.exc_info(), '\n')
                return [], visited

        for link in link_list_final:
            if link not in visited:
                url_root = url_regex(link,1 ,2)
                print('Depth: {} Max: {} Link: {}'.format(depth, max_depth, link))
                link_list_preprocess, visit = main(link, max_depth, depth + 1, url_root, link_list_final, visited, robots, rude)

                # Add processed link to final link list
                if link not in link_list_ultimate:
                    link_list_ultimate.append(link)

                # Add any found sub links to final link list
                for itm in link_list_preprocess:
                    if itm not in link_list_ultimate:
                        link_list_ultimate.append(itm)

                # Used to cary link_list_final from one level to another
                for itm in url_buff:
                    if itm not in link_list_ultimate:
                        link_list_ultimate.append(itm)

                # Used to carry visited list from one recursion level to another
                for itm in visit:
                    if itm not in visited:
                        visited.append(itm)

        return link_list_ultimate, visited

    elif url in visited:
        return [], visited

    else:
        visited.append(url)
        return [url], visited

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
        print('Usage: {} <parent url to scan>'.format(sys.argv[0]))
        print('Enter {} --help for more info'.format(sys.argv[0]))
        sys.exit()

    # Look for help string option
    elif '--help' in sys.argv:
        print(help_str)
        sys.exit()

    else:
        # Init variables for main function
        # Modified below if needed
        max_depth = 2
        robo_avoid = []
        robots = []
        rude = False
        args = sys.argv[1:]
        path_exists = True

        # Look for custom max scan depth
        if '-m' in args:
            max_depth = int(args[args.index('-m') + 1])
            args.pop(args.index('-m') + 1)
            args.pop(args.index('-m'))
        
        # Look to see if user wants to be rude
        if '-r' in args:
            args.pop(args.index('-r'))
            rude = True 

        else:
            robo_avoid = robo_text(args[0])
            robots.append(args[0])

        try:
            # extract root URL ex. http://www.google.com -> google.com
            rooturl = url_regex(args[0],2 ,2)
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
            if os.path.exists(filepath + rooturl + num + '.txt'):
                num = '(' + str(idx) + ')'
                idx += 1

            else:
                file_out = filepath + rooturl + num + '.txt'
                path_exists = False

        # Write harvested links to file
        with open(file_out, 'a') as urltext: 
            for line in url_out:
                urltext.write(line + '\n')
