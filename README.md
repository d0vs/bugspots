# bugspots

## What is bugspots?

Bugspots is a Python implementation of
[the bug prediction algorithm used at Google][1].
It also embed a command-line interface which can be used to list the "hot spots"
of a Git repository.

 [1]: http://google-engtools.blogspot.com/2011/12/bug-prediction-at-google.html

## What is a hot spot?

A hot spot is a file where bugs tend to be introduced in a more significant
matter.

## How does it work?

The algorithm is very simple and to the point: it gives each file a score based
on its number of bug-fixing commits and their age, and then return a
descending-ordered list of the files based on their score, filtering commits
that are no longer at `HEAD`.

### What is a bug-fixing commit?

Any commit whose purpose is to fix an issue.  They are identified by message,
using [the same pattern as GitHub][2], which is:

	(?i)(fix(e[sd])?|close[sd]?) #[1-9][0-9]*

 [2]: https://github.com/blog/831-issues-2-0-the-next-generation

### What is the formula used?

	score = Sum[1 / (1 + e^(-12 * t_i + 12)), i=0, n]

where *t_i* is the timestamp of the *i*th commit, normalized between 0 and 1
(0 being the date of the first commit in the repository and 1 being the date of
the last commit in the repository), and *n* is the number of bug-fixing commits.

## Installation

	$ pip install bugspots

## Command-line usage

	$ bugspots.py -h

## Python example

	import bugspots
	
	b = bugspots.Bugspots()
	for hotspot in b.get_hotspots():
	    print " %6.3f %s" % (hotspot.score, hotspot.filename)
