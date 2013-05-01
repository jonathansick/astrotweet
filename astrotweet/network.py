#!/usr/bin/env python
# encoding: utf-8
"""
Build and analyze networks of mutual followers in the astronomy community.
"""

import networkx as nx


def construct_graph(c):
    """Construct a graph of mutual friends (connected notes are both frields
    and followers of each other). A NetworkX graph is returned.
    
    Our algorithm is to loop through each user in the community,
    and find matches (intersections) in the user's `friend_ids` and
    `follower_ids` lists.

    This is inspired by Example 4-10 from *Mining the Social Web* by
    M. A. Russell.
    """
    g = nx.Graph()
    # Get all users who both follow and are followed
    q = {"friend_ids": {"$exists": 1}, "friends_count": {"$gt": 0},
            "follower_ids": {"$exists": 1}, "followers_count": {"$gt": 0}}
    cursor = c.find(q, fields=['friend_ids', 'follower_ids'], timeout=False)
    for doc in cursor:
        currentID = doc['_id']
        friendSet = set(doc['friend_ids'])
        followerSet = set(doc['follower_ids'])
        for friendID in friendSet & followerSet:  # Loop over intersection!
            g.add_edge(currentID, friendID)
    return g


def main():
    import pymongo
    conn = pymongo.MongoClient('localhost', 27017)
    c = conn['astrotweet']['users']
    construct_graph(c)


if __name__ == '__main__':
    main()
