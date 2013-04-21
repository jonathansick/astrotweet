import logging
import re

import requests
from cliff.lister import Lister


class ListHandles(Lister):
    """Show a list of files in the current directory.

    The file name and size are printed by default.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        usernames = get_handles()
        # print usernames
        return (('handle', "URL"), ((usr, user_url(usr)) for usr in usernames))


def user_url(username):
    return "http://www.twitter.com/%s" % username


def get_handles():
    """docstring for get_handles"""
    url = 'http://www.astrobetter.com/wiki/tiki-index.php?page=Astronomers+on+Twitter'
    r = requests.get(url)
    txt = r.text
    # See http://shahmirj.com/blog/extracting-twitter-usertags-using-regex
    # for a twitter username regex
    pattern = r'(?<=^|(?<=[^a-zA-Z0-9-_\\.]))@([A-Za-z]+[A-Za-z0-9_]+)'
    usernames = re.findall(pattern, txt)
    usernames.sort()
    return usernames
