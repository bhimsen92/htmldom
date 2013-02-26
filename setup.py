from distutils.core import setup

setup(
	name = "htmldom",
	packages = ['htmldom'],
	version = '2.0',
	description = 'HTML parser which can be used for web-scraping applications',
	long_description = 'htmldom parses the HTML file and provides methods for iterating and searching and modifying the parse tree in a similar way as Jquery',
	author = 'Bhimsen.S.Kulkarni',
	author_email = 'bhimsen.pes@gmail.com',
	url = 'http://pypi.python.org/',
	license = 'FreeBSD License',
	platforms = 'Linux',
	classifiers = [
	                 'Development Status :: 4 - Beta',
	                 'Programming Language :: Python :: 3.2',
	                 'License :: OSI Approved :: BSD License ',
	                 'Operating System :: POSIX :: Linux',
	                 'Environment :: Web Environment',
	                 'Intended Audience :: Developers',
	                 'Topic :: Software Development :: Libraries :: Python Modules',
	                 'Topic :: Text Processing :: Markup :: HTML'
	              ]);
