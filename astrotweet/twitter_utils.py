#!/usr/bin/env python
# encoding: utf-8
"""
Interface to the twitter API for looking up user data.

2013-04-21 - Created by Jonathan Sick
"""

import time
import twitter
import datetime
import json
import os


def read_credentials():
    """Read the app's consumer key and oauth tokens from ~/.astrotweet.json
    
    Credentials can be obtained from https://dev.twitter.com/apps/new/
    The format of this JSON document should be::

        {
            "consumer_key": "your_consumer_key,
            "consumer_secret": "your_consumer_secret",
            "oauth_token": "your_access_token",
            "oauth_token_secret": "your_access_token_secret"
        }
    
    """
    path = os.path.expanduser("~/.astrotweet.json")
    f = open(path, 'r')
    creds = json.load(f)
    f.close()
    return creds


def connect():
    """Create a twitter instance, connected to v1.1 of the API with OAuth
    authentication.
    """
    c = read_credentials()
    auth = twitter.oauth.OAuth(c['oauth_token'], c['oauth_token_secret'],
                               c['consumer_key'], c['consumer_secret'])
    t = twitter.Twitter(domain='api.twitter.com',
        api_version='1.1',
        auth=auth)
    return t


def lookup_users(usernames):
    """Given a list of twitter usernames, returns a dictionary of twitter
    user profiles."""
    users = {}
    t = connect()
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
            elif t.application.rate_limit_status()['resources']['users']['/users/lookup']['remaining'] == 0:
                status = t.application.rate_limit_status()['resources']['users']['/users/lookup']
                now = time.time() # UTC
                whenRateLimitResets = status['reset'] # UTC
                sleepTime = whenRateLimitResets - now
                print 'Rate limit reached. Trying again in %i seconds' % (sleepTime, )
                time.sleep(sleepTime)
                continue
    return userData


def get_friends_ids(screenName=None, idstr=None, maxFriends=10000):
    """Given a user screen name or `id_str`, return a list of the user's
    friends (who the person follows). Each friend is an `id_str`."""
    t = connect()
    args = {"stringify_ids": True}
    if screenName is not None:
        args['screen_name'] = screenName
    elif idstr is not None:
        args['user_id'] = idstr
    else:
        # TODO throw exception
        pass
    cursor = -1
    ids = []
    waitPeriod = 2.
    while cursor != 0:
        args['cursor'] = cursor
        try:
            result = t.friends.ids(**args)
            ids.extend(result['ids'])
            cursor = result['next_cursor']
            if len(ids) >= maxFriends: break
        except twitter.api.TwitterHTTPError, e:
            if e.e.code == 401:
                print 'Encountered 401 Error (Not Authorized)'
                break
            elif e.e.code in (502, 503):
                print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code, waitPeriod)
                time.sleep(waitPeriod)
                waitPeriod *= 1.5
                continue
            elif t.application.rate_limit_status()['resources']['friends']['/friends/ids']['remaining'] == 0:
                status = t.application.rate_limit_status()['resources']['friends']['/friends/ids']
                now = time.time() # UTC
                whenRateLimitResets = status['reset'] # UTC
                sleepTime = whenRateLimitResets - now
                print 'Rate limit reached. Trying again in %i seconds' % (sleepTime, )
                time.sleep(sleepTime)
                continue
    return ids


def get_follower_ids(screenName=None, idstr=None, maxFollowers=10000):
    """Given a user screen name or `id_str`, return a list of the user's
    followers. Each follower is an `id_str`.
    
    :param maxFollowers": maximum number of followers to be returned.
    """
    t = connect()
    args = {"stringify_ids": True}
    if screenName is not None:
        args['screen_name'] = screenName
    elif idstr is not None:
        args['user_id'] = idstr
    else:
        # TODO throw exception
        pass
    cursor = -1
    ids = []
    waitPeriod = 2.
    while cursor != 0:
        args['cursor'] = cursor
        try:
            result = t.followers.ids(**args)
            ids.extend(result['ids'])
            cursor = result['next_cursor']
            if len(ids) >= maxFollowers: break
        except twitter.api.TwitterHTTPError, e:
            if e.e.code == 401:
                print 'Encountered 401 Error (Not Authorized)'
                break
            elif e.e.code in (502, 503):
                print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code, waitPeriod)
                time.sleep(waitPeriod)
                waitPeriod *= 1.5
                continue
            elif t.application.rate_limit_status()['resources']['followers']['/followers/ids']['remaining'] == 0:
                status = t.application.rate_limit_status()['resources']['followers']['/followers/ids']
                now = time.time() # UTC
                whenRateLimitResets = status['reset'] # UTC
                sleepTime = whenRateLimitResets - now
                print 'Rate limit reached. Trying again in %i seconds' % (sleepTime, )
                time.sleep(sleepTime)
                continue
    return ids


def str_to_datetime(createdAt):
    """Convert a twitter timestamp (often a ``created_at`` field) to a datetime.
    
    See: http://stackoverflow.com/a/8825799
    """
    return datetime.datetime.strptime(createdAt, '%a %b %d %H:%M:%S +0000 %Y')


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    via http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


if __name__ == '__main__':
    # creds = read_credentials()
    # print creds
    t = connect()
    print lookup_users(['jonathansick','angryastropanda'])
    status = t.application.rate_limit_status()
    print json.dumps(status, sort_keys=True, indent=1)
    print status['resources']['users']['/users/lookup']
    print get_friends_ids(screenName='jonathansick')
    print get_follower_ids(screenName='jonathansick')
