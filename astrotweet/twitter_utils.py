#!/usr/bin/env python
# encoding: utf-8
"""
Interface to the twitter API for looking up user data.

2013-04-21 - Created by Jonathan Sick
"""

import time
import twitter


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
