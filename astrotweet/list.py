import logging
import time
import re
import os

import requests
import twitter
from cliff.command import Command


class ListHandles(Command):
    """Show a list of files in the current directory.

    The file name and size are printed by default.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        usernames = get_handles()
        # usernames = usernames[:2]  # DEBUG
        userData = lookup_users(usernames)
        usernames = userData.keys()
        usernames = sorted(usernames,
                key=lambda n: userData[n]['followers_count'])[::-1]
        # TODO accept argument for filename
        self._write_dataset(userData, usernames, "astrotweeters.csv")

    def _write_dataset(self, data, usernames, filepath):
        """Write the astrotweeter data set as a CSV file."""
        fields = ('screen_name', 'name', 'location', 'url',
                'friends_count', 'followers_count', 'statuses_count')
        lines = ["# %s" % "\t".join(fields)] \
                + [self._write_line(data[n], fields) for n in usernames]
        txt = "\n".join(lines)
        if os.path.exists(filepath): os.remove(filepath)
        f = open(filepath, 'w')
        f.write(txt.encode('utf8'))
        f.close()

    def _write_line(self, data, fields):
        """Form text line for a single user"""
        # Ugly code to munge the data into a tab-delimited-amenable format
        values = []
        for f in fields:
            v = unicode(data[f])
            v = v.replace("\n", " ")
            v = v.replace("\t", " ")
            values.append(v)
        return "\t".join(values)


def user_url(username):
    """Form the profile URL of a twitter user given a screen name."""
    return "http://www.twitter.com/%s" % username


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


def lookup_users(usernames):
    """Given a list of twitter usernames, returns a dictionary of twitter
    user profiles."""
    users = {}
    t = twitter.Twitter(domain='api.twitter.com', api_version='1')
    for usrBatch in chunks(usernames, 100):
        usrBatch = list(usrBatch)
        dataBatch = _lookup_user_batch(t, usrBatch)
        users.update(dataBatch)
    return users


def _lookup_user_batch(t, usrBatch):
    """Lookup profiles from a batch of screen names
    
    Much of this code is borrowed from *Mining the Social Web* by
    Matthew Russell.
    """
    screenNameList = ",".join(usrBatch)
    incomplete = True
    waitPeriod = 2.
    while incomplete:
        try:
            responses = t.users.lookup(screen_name=screenNameList)
            userData = {r['screen_name']: r for r in responses}
            incomplete = False
        except twitter.api.TwitterHTTPError, e:
            if e.e.code == 401:
                print 'Encountered 401 Error (Not Authorized)'
                userData = {}
                incomplete = False
            elif e.e.code in (502, 503):
                print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code, waitPeriod)
                time.sleep(waitPeriod)
                waitPeriod *= 1.5
                continue
            elif t.account.rate_limit_status()['remaining_hits'] == 0:
                status = t.account.rate_limit_status()
                now = time.time() # UTC
                whenRateLimitResets = status['reset_time_in_seconds'] # UTC
                sleepTime = whenRateLimitResets - now
                print 'Rate limit reached. Trying again in %i seconds' % (sleepTime, )
                time.sleep(sleepTime)
                continue
    return userData


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    via http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
