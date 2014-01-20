First, download and install mercurial here:
http://mercurial.selenic.com/downloads/

Then download and install appengine libraries here:
https://developers.google.com/appengine/downloads

And open the app at least once, to set up /usr/local/google_appengine.

Then to set up dancedeets, run ./setup.sh first. It will download and install
the necessary libraries, setting up symlinks for the ones that need to be
included in the uploaded package.

Once that's done, run 'make' to compile the templates.  This must be done after
every change to the templates/ directory.

Finally, you can run ./nose.sh to run all of the included tests. Some of them
actually talk to google maps API server (and form a regression test to ensure we
understand the returned data).  As such, if you run the tests too often you may
encounter quota-exceeded errors.  Just wait a bit before re-running tests, or
pass in a directory/filename to limit the scope of tests that are run.
