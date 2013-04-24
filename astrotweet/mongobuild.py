#!/usr/bin/env python
# encoding: utf-8
"""
Build a MongoDB collection of Astro Twitter users.

2013-04-23 - Created by Jonathan Sick
"""

import logging
import datetime

from pymongo import MongoClient
from cliff.command import Command

from wikireader import get_handles
from twitter_utils import lookup_users, str_to_datetime


class MongoBuilder(Command):
    """Command for building a MongoDB collection of twitter users."""

    log = logging.getLogger(__name__)

    def get_parser(self, progName):
        parser = super(MongoBuilder, self).get_parser(progName)
        parser.add_argument(
            "--host", action='store', default='localhost')
        parser.add_argument(
            "--port", action='store', default=27017, type=int)
        parser.add_argument(
            "--dbname", action='store', default='astrotweet')
        parser.add_argument(
            "--cname", action='store', default='users')
        return parser

    def take_action(self, parsedArgs):
        """Run the mongo builder pipeline."""
        conn = MongoClient(parsedArgs.host, parsedArgs.port)
        self.c = conn[parsedArgs.dbname][parsedArgs.cname]
        newHandles = self._get_new_handles()
        if len(newHandles) == 0:
            self.log.info("No new users to add")
        else:
            userData = lookup_users(newHandles)
            for screenName, userDict in userData.iteritems():
                self._insert_user(userDict)

    def _get_new_handles(self):
        """Get user handles from the AstroBetter wiki that are not yet in
        MonogoDB.

        The implementation is a bit messy here; can we run fewer mongodb
        lookups?
        """
        allHandles = get_handles()
        newHandles = []
        for handle in allHandles:
            if self.c.find({'screen_name': handle}).count() == 0:
                newHandles.append(handle)
        return newHandles

    def _insert_user(self, userDict):
        """Add a single user to users collection. `userDict` is a dictionary
        of data for a single from the Twitter API users/lookup function.
        """
        # Retain on a subset of keys from API lookup result
        keys = ['description', 'profile_image_url', 'followers_count',
                'location', 'statuses_count', 'friends_count',
                'screen_name', 'id', 'lang',
                'favourites_count', 'name',
                'url', 'created_at', 'listed_count']
        doc = {k: userDict[k] for k in keys}
        doc['created_at'] = str_to_datetime(userDict['created_at'])
        # Use updated_at as record of when user info was retrieved
        doc['updated_at'] = datetime.datetime.now()
        # _id is the twitter id number as a string
        doc['_id'] = userDict['id_str']
        self.log.debug(doc)
        self.log.info("Inserting %s" % doc['screen_name'])
        self.c.save(doc)
