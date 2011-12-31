#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Bugspots is a Python implementation of the bug prediction algorithm used at
Google. (see http://bitly.com/uglCGz)

You can use its command-line interface to identify hot spots in a Git
repository::

	~dev/git/jquery$ bugspots.py
	Scanning repository...
	Found 6 hot spots
	
	 2.581 src/event.js
	 1.912 src/css.js
	 1.420 test/unit/event.js
	 1.115 test/unit/css.js
	 0.996 src/manipulation.js
	 0.906 src/effects.js

"""

from __future__ import division

__author__ = "A.B."
__version__ = "0.1"
__license__ = "ISC License"

class Bugspots:
	"""Implementation of the bug prediction algorithm used at Google."""
	
	def __init__(self, branch="master", depth=500,
	             grep="(fix(e[sd])?|close[sd]?) #[1-9][0-9]*"):
		"""
		Initialize object.
		
		:param branch: Branch to crawl
		:param depth: Depth of the log crawl
		:param grep: Regular expression filter (not case-sensitive)
		
		"""
		self._branch = branch
		self._depth = depth
		self._grep = grep
	
	def _get_commits(self):
		"""Return matching commits among the last `self._depth` ones."""
		# TODO: filter files that are no longer at HEAD
		import git
		import re
		
		repo = git.Repo(".")
		commits = list()
		
		for commit in repo.iter_commits(self._branch, max_count=self._depth):
			if re.search(self._grep, commit.message, re.I):
				commits.append(dict(time=commit.committed_date,
				                    filenames=commit.stats.files.keys()))
		
		return commits
	
	def get_hot_spots(self):
		"""Return the top 10% hot spots."""
		import collections
		import time
		import math
		import operator
		
		commits = self._get_commits()
		scores = collections.defaultdict(int)
		
		first_commit_time = commits[-1]["time"]
		repo_age = int(time.time()) - first_commit_time
		
		for commit in commits:
			ti = ((commit["time"] - first_commit_time) / repo_age)
			
			for filename in commit["filenames"]:
				scores[filename] += 1 / (1 + math.exp(-12 * ti + 12))
		
		hot_spots = sorted(scores.iteritems(), key=operator.itemgetter(1),
		                   reverse=True)
		return hot_spots[:len(hot_spots) // 10]

if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description="""Bugspots is a Python implementation of the bug
		prediction algorithm used at Google.""")
	parser.add_argument("-b", "--branch", help="branch to crawl")
	parser.add_argument("-d", "--depth", type=int, help="""depth of the log
	                    crawl""")
	parser.add_argument("--grep", help="""only select commits that matches the
	                    specified regular expression (not case-sensitive)""",
	                    metavar="FILTER")
	parser.add_argument("-V", "--version", action="version",
		                version="bugspots %s" % __version__)
	parser.set_defaults(branch="master", depth=500,
	                    grep="(fix(e[sd])?|close[sd]?) #[1-9][0-9]*")
	
	args = parser.parse_args()
	b = Bugspots(branch=args.branch, depth=args.depth, grep=args.grep)
	
	print "Scanning repository..."
	
	hot_spots = b.get_hot_spots()
	print "Found %d hot spots\n" % len(hot_spots)
	
	for i in hot_spots:
		print " %.3f %s" % (i[1], i[0])
