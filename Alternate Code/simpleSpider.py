#!/usr/bin/env python3

import requests
import re

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

res = list(set(scrape('https://dinkyouverymuch.com')))

res.sort()

with open('spiderOut.txt', 'w') as f:
    for x in res:
        f.write(x + "\n")
