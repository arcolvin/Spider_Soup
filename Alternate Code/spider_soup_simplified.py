#!/usr/bin/env python3

import urllib.request as urlreq
from bs4 import BeautifulSoup
import sys
import re
import os
import codecs

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
    Contain the passed variables inside a class

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

If you have pip use:
sudo pip install bs4

A text file located within ~/Spider_Soup/ will be written with your results.
The text file should have the domain name for the root web page scanned.

command ex. {} http://www.example.com -m 2 -r
            {} -r http://www.example.com -m 3
            {} -m 4 http://www.example.com
            {} http://www.example.com

Thank you for using Spider_Soup!


'''.format(sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])


class Spider:
    def __init__(self):
        self.url = ''
        self.max_depth = 2
        self.depth = 0
        self.url_root = ''
        self.url_buff = set()
        self.url_list = set()
        self.visited = set()
        self.robots = set()
        self.master = set()
        self.rude = False


def main(spider):

    # Main function for parseing the web pages
    html_soup = ''
    spider.url_root = url_regex(spider.url, 1, 2)
    # if we only provide root url's we can eliminate a function call
    # further down where robo txt is called
    for url in robo_text(spider.url_root):
        spider.visited.add(url)

    if spider.depth <= spider.max_depth and spider.url not in spider.visited:
        # this may be the problem with chaining deeper
        # or with reaching the hidden test page in rude mode
        spider.visited.add(spider.url)
        spider.master.add(spider.url)

        # attempt to call the user given URL to look for links
        try:
            headers = {'User-Agent': "Mozilla/5.0"}
            req = urlreq.Request(spider.url, None, headers)
            html = urlreq.urlopen(req).read()

        # Return user friendly error if web address is no good
        except ValueError:
            print()
            print('\nInvalid URL found while building html doc')
            print('Working with {}\n'.format(spider.url))

        # permit the user to end the program with ctrl + c
        except KeyboardInterrupt:
            sys.exit()

        # Return generic error message if unexpected error occurs
        except:
            print('\nException occurred while trying to build HTML doc')
            print('Working with {}\n'.format(spider.url))
            print('\n', sys.exc_info(), '\n')

            # Original Return statement remove when code is working
            # return [], spider.visited
            spider.depth -= 1
            return spider

        # Parse HTML code into workable document
        html_soup = BeautifulSoup(html, 'html.parser')

        # find all links in HTML doc
        for link in html_soup.find_all('a'):
            spider.url_buff.add(link.get('href'))

        # assemble links into http(s):// form
        # discard unusable links
        for link in spider.url_buff:
            try:
                # look for relative links ex. /index.html
                if link[0] == '/' and len(link) > 1:
                    spider.master.add(spider.url_root + link)
                    spider.url_list.add(spider.url_root + link)

                # look for full links ex. http://www.example.com
                elif link[0:4].upper() == 'HTTP' or link[0:3].upper() == 'FTP':
                    spider.master.add(link)
                    spider.url_list.add(link)

                    # If given absolute URL, respect robots.txt
                    ''' FIX HERE DO WE NEED ROBOTS STILL? '''
                    if spider.url_root not in spider.robots and \
                            spider.rude is False:
                        robo_avoid = robo_text(link)
                        for itm in robo_avoid:
                            spider.visited.add(itm)
                        spider.robots.add(url_regex(link, 1, 2))

                # Ignore root links ex. /
                elif link[0] == '/' and len(link) == 1:
                    continue

                # look for relative links not starting in "/" ex. index.php
                else:
                    if (spider.url_root + '/' + link) not in spider.master \
                            and (spider.url_root + '/' + link) not in \
                            spider.visited:
                        spider.url_list.add(spider.url_root + '/' + link)

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

                # Original return statement remove once working
                # return [], visited
                spider.depth -= 1
                return spider

        for link in spider.url_list:
            if link not in spider.visited:
                spider.url_root = url_regex(link, 1, 2)
                print('Depth: {} Max: {} Link: {}'
                      .format(spider.depth, spider.max_depth, link))

                spider_in = spider
                spider_in.url_buff = set()
                spider_in.url_list = set()
                spider_in.depth += 1
                spider_in.url = link

                spider_out = main(spider_in)

                del spider_in

                # Add processed link to final link list
                spider.master.add(link)

                # Add any found sub links to final link list
                for itm in spider_out.master:
                    spider.master.add(itm)

                # Cary link_list_final from one level to another
                for itm in spider.url_list:
                    spider.master.add(itm)

                # Carry visited list from one recursion level to another
                for itm in spider_out.visited:
                    spider.visited.add(itm)

                del spider_out

        spider.depth -= 1
        return spider

    elif spider.url in spider.visited:
        spider.depth -= 1
        return spider

    else:
        spider.visited.add(spider.url)
        spider.depth -= 1
        return spider


def robo_text(url):
    robo_avoid = []

    # extract root url
    url = url_regex(url, 1, 2)

    # Attempt to call the URL to find robot.txt entries
    try:
        headers = {'User-Agent': "Mozilla/5.0"}
        req = urlreq.Request(url + '/robots.txt', None, headers)
        html = urlreq.urlopen(req)
        for line in html:
            robo_rule = ''
            robo_obj = re.match(r'[^\/]+(\/\S+)',
                                line.decode('unicode_escape'))
            try:
                robo_rule = line[robo_obj.start(1):robo_obj.end(1)] \
                    .decode('unicode_escape')
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
    # ex. for http://www.example.com/index.html
    #       (1)(http://www.) (2)(example.com) (3)(/index.html)
    urlobj = re.match(
        r'((?:https?|ftp)://(?:[a-zA-Z]+\.)?)?([^/\r\n]+)(/[^\r\n]*)?', url)
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
    elif '--help' in sys.argv or '-h' in sys.argv or '?' in sys.argv:
        print(help_str)
        sys.exit()

    else:
        # Create initial spider
        # Place arguments into workable list
        spider = Spider()
        args = sys.argv[1:]

        # Look for custom max scan depth
        if '-m' in args:
            spider.max_depth = int(args[args.index('-m') + 1])
            args.pop(args.index('-m') + 1)
            args.pop(args.index('-m'))

        # Look to see if user wants to be rude
        if '-r' in args:
            args.pop(args.index('-r'))
            spider.rude = True

        else:
            # Set parent url
            spider.url = args[0]

            """
            # Process robots.txt if present
            for url in robo_text(spider.url):
                spider.visited.add(url)
            # Remove below line if not needed in final program
            '''spider.robots.add(args[0])'''
            """

        try:
            # extract root URL ex. http://www.google.com -> google.com
            filename = url_regex(spider.url, 2, 2)

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
        filepath = os.path.expanduser('~/Spider_Soup_Output/')

        # Check to see if output folder exists and create if not
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Call main function to run recursively and spider the web page
        output = main(spider)

        # -----------------Code here after Main finished----------------
        # Sort output for writing to final file
        '''
        Since final url list is being stored in a set we need to
        extract all url's into a list to organize them.
        Once extracted use organized list to save url's to a file.
        '''

        # This needs to be changed to match above docsting
        final_url_list = []
        for url in output.master:
            final_url_list.append(url)
        final_url_list.sort()

        # Create alternate filenames if file exists already
        num = ''
        idx = 2
        path_exists = True
        while path_exists is True:
            if os.path.exists(filepath + filename + num + '.txt'):
                num = '(' + str(idx) + ')'
                idx += 1

            else:
                file_out = filepath + filename + num + '.txt'
                path_exists = False

        # Write harvested links to file
        with open(file_out, 'a') as urltext:
            for line in final_url_list:
                urltext.write(line + '\n')

        print('Found links written to: {}'.format(file_out))
