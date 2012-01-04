#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 textwidth=79
"""
Bugspots is a Python implementation of the bug prediction algorithm used at
Google and it embed a command-line interface.

"""
from __future__ import division

import subprocess
import itertools
import collections
import os
import math
import operator

__author__ = "A.B."
__version__ = "0.1"
__license__ = "ISC License"

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Hotspot(Bunch):
    """
    Class representing a hot spot.
    
    This class must be called with the following keyword arguments:
    
    :py:attr:`filename`: Filename.
    :py:attr:`score`: Score returned by :py:meth:`Bugspots._get_score`.
    
    """
    pass

class File(Bunch):
    """
    Class representing a file.
    
    This class must be called with the following keyword arguments:

    :py:attr:`name`: Filename.
    :py:attr:`commit_dates`: List of timestamps.
    
    """
    pass

class Bugspots(object):
    """Implementation of the bug prediction algorithm used at Google."""
    
    def __init__(self, path=".", depth=500,
                 grep="(fix(e[sd])?|close[sd]?) #[1-9][0-9]*"):
        """
        Constructor.
        
        :param string path: Path to the Git repository.
        :param integer depth: Depth of the log crawl.
        :param string grep: Case insensitive regular expression used to match
                            commits.
        
        """
        self._path = path
        self._depth = depth
        self._grep = grep
    
    def _get_files(self):
        """
        Return a list of matching files.
        
        :rtype: list of :py:obj:`File` objects
        
        """
        head_filenames = set(
            subprocess.check_output(["git", "ls-tree", "HEAD", "--name-only",
                                     "-r"]).strip().split("\n"))
        
        files = collections.defaultdict(list)
        popenargs = ["git", "log", "-%d" % self._depth, "--format=format:%ct",
                     "--name-only", "-E", "-i", "--grep=%s" % self._grep,
                     "--diff-filter=ACDMRTUXB"]
        
        for commit in subprocess.check_output(popenargs).strip().split("\n\n"):
            data = commit.split("\n")
            commit_date, filenames = data[0], set(data[1:])
            for filename in itertools.ifilter(lambda s: s in head_filenames,
                                              filenames):
                files[filename].append(int(commit_date))
        
        return [File(name=k, commit_dates=v) for k, v in files.iteritems()]
    
    def _get_score(self, f, repo_start, repo_age):
        """
        Return the score of a given file.
        
        :param :py:obj:`File` f: A :py:obj:`File` object.
        :param integer repo_start: Timestamp of the first matching commit.
        :param integer repo_age: Timespan of the matching commits in seconds.
        
        :rtype: float
        
        """
        def normalize_timestamp(timestamp):
            return (timestamp - repo_start) / repo_age
        return sum(1 / (1 + math.exp(-12 * normalize_timestamp(t) + 12))
                   for t in f.commit_dates)
    
    def get_hotspots(self):
        """
        Return the top 10% hot spots.
        
        :rtype: list of :py:obj:`Hotspot` objects
        
        """
        prev_path = os.getcwd()
        os.chdir(self._path)
        
        repo_start = int(subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", "-E", "-i",
             "--grep=%s" % self._grep, "--diff-filter=ACDMRTUXB"]))
        repo_end = int(subprocess.check_output(
            ["git", "log", "-%d" % self._depth, "--format=%ct", "-E", "-i",
             "--grep=%s" % self._grep, "--diff-filter=ACDMRTUXB",
             "--reverse"]).split("\n")[0])
        repo_age = repo_end - repo_start
        
        files = self._get_files()
        os.chdir(prev_path)
        
        return sorted([Hotspot(filename=f.name,
                               score=self._get_score(f, repo_start, repo_age))
                       for f in files],
                      key=operator.attrgetter("score"),
                      reverse=True)[:len(files) // 10]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Bugspots is a Python implementation of the bug "
        "prediction algorithm used at Google.")
    
    parser.add_argument("-d", "--depth", type=int,
                        help="depth of the log crawl", default=500)
    parser.add_argument("--grep", help="non-case-sensitive regular expression "
                        "used to match commits",
                        default="(fix(e[sd])?|close[sd]?) #[1-9][0-9]*")
    
    parser.add_argument("-V", "--version", action="version",
                        version="bugspots %s" % __version__)
    
    args = parser.parse_args()
    
    b = Bugspots(depth=args.depth, grep=args.grep)
    print "Scanning repository..."
    
    hotspots = b.get_hotspots()
    print "Found %d hot spots\n" % len(hotspots)
    
    for hotspot in hotspots:
        print " %6.3f %s" % (hotspot.score, hotspot.filename)
