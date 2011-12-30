from distutils.core import setup
import bugspots

setup(
	name="bugspots",
	version=bugspots.__version__,
	description="""Identify hot spots in a codebase with the bug prediction
	algorithm used at Google.""",
	long_description=bugspots.__doc__,
	author=bugspots.__author__,
	author_email="bmbslice@gmail.com",
	url="http://pypi.python.org/pypi/bugspots",
	py_modules=["bugspots"],
	license=bugspots.__license__,
	platforms="Unix",
	classifiers=[
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: ISC License (ISCL)",
		"Natural Language :: English",
		"Operating System :: Unix",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: Implementation :: CPython",
		"Topic :: Software Development :: Bug Tracking",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Utilities"
	]
)
