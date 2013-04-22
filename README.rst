==================================================================
astrotweet - Work with AstroBetter's Index of Tweeting Astronomers
==================================================================

This is a project to build on `AstroBetter's index of tweeting astronomers. <http://www.astrobetter.com/wiki/tiki-index.php?page=Astronomers+on+Twitter/>`_ 
Some things that we *will* eventually do include:

- building and updating a twitter list of astronomers
- machine-readable analytics of astronomy tweeters, including number of tweets or followers.


Installation
------------

Download the code and run ``setup.py install``.

You'll need the following third-party packages: ``Cliff``, ``requests`` and ``twitter``.
Pip should install these automatically.
To check your installation run::

    astrotweet --help


Commands
--------

``astrotweet`` is a command line app built around the philosophy of subcommands, much like ``git``.
Here are the commands currently included in ``astrotweet``:

- ``astrotweet summary`` - will output a summary table (tab-separated) of astrotweeters to the file ``astrotweeters.csv``. Columns include 'real' name, follower counts, etc..


About
-----

This is hack by Jonathan Sick. Tweet: @jonathansick
