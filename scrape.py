#!/usr/bin/env python3
# Version: 0.1

import sys
import os
import spider

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

def writeOut(url_out):
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

        try:
            # extract root URL ex. http://www.google.com -> google.com
            rooturl = crawler.url_regex(args[0],2 ,2)
        except AttributeError:
            print('Invalid URL')
            print('Use full url such as: https://www.google.com')
            sys.exit()

        except:
            print('Exception occurred! See exception info below')
            print('Trying to extract root URL\n')
            print(sys.exc_info())
            sys.exit()

        # Call main function to run recursively and spider the web page
        urls, visited = crawler.scrape()

        # Sort output for writing to final file
        list(urls)
        urls.sort()
