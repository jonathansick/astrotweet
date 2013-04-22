#!/usr/bin/env python
# encoding: utf-8
"""
Read twitter handles from AstroBetter's index of tweeting astronomers.

2013-04-21 - Created by Jonathan Sick
"""

import requests
import re


def get_handles():
    """Scrape the twitter handles from the AstroBetter wiki."""
    url = 'http://www.astrobetter.com/wiki/tiki-index.php?page=Astronomers+on+Twitter'
    r = requests.get(url)
    txt = r.text
    # See http://shahmirj.com/blog/extracting-twitter-usertags-using-regex
    # for a twitter username regex
    pattern = r'(?<=^|(?<=[^a-zA-Z0-9-_\\.]))@([A-Za-z]+[A-Za-z0-9_]+)'
    usernames = re.findall(pattern, txt)
    usernames.sort()
    return usernames
