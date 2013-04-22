import logging
import os

from cliff.command import Command

from wikireader import get_handles
from twitter_utils import lookup_users


class SummaryTable(Command):
    """Command to write a summary table of astro tweeters from the AstroBetter
    list to astrotweeters.csv.
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
