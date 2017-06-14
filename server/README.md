[![Build Status](https://travis-ci.org/mikelambert/dancedeets-monorepo.svg?branch=master)](https://travis-ci.org/mikelambert/dancedeets-monorepo)

[![Coveralls](https://coveralls.io/repos/mikelambert/dancedeets/badge.svg?branch=master&service=github)](https://coveralls.io/github/mikelambert/dancedeets?branch=master)

# DanceDeets

The magic behind <http://www.dancedeets.com/>.

## Setup

First, download and install appengine libraries here:
<https://developers.google.com/appengine/downloads>
...and open the AppEngine app at least once, to set up /usr/local/google_appengine.

Second, setup gcloud:
```
curl https://sdk.cloud.google.com | bash
gcloud components update app preview
gcloud config set project dancedeets-hrd
gcloud auth login
gcloud app run app.yaml
```

Third, to setup dancedeets, run `./setup.sh`. It will download and install libraries,
and setup some in our lib/ directory for uploading to appengine.

You can run a variety of commands from gulp:
- `gulp test` to run all of the included tests.
- `gulp server:hot` to run a local server
- `gulp deployServer` to push to production

If you are running the NLP classifier evaluations, you may want to setup re2 for speed.
To do this, download/install from <https://github.com/google/re2/>
Then install `pip install re2` to get the python wrappers.

## Code Layout

- `assets/`: The Frontend code, used by Webpack to build out the JS, CSS, and Images (written into `dist/`)
- `amp/`: Google AMP support tools
- `brackets/`: Show youtube videos in a nice battle display format (exploratory code)
- `battle_brackets/`: Handle the server-side of the Battle Brackets I was building on mobile (exploratory code)
- `classes/`: Scrape and display the Class schedules in LA and NYC
- `classifiers/`: Help tune and tweak the keyword-based classifier. Not worth worrying about unless making changes there
- `docker/`: The docker images used by our project (Should set these up using `gulpfile.babel.js`)
- `event_attendees/`: The attendee-based event classifier
- `event_scraper/`: Scrapes the FB pages/groups, as well as the signed-in users' events, to find and classify events
- `events/`: Event code (locations, reloading, adding/removing, images, etc). Everything not classifier/scraping-related.
- `favorites/`: First attempt at setting up event-favoriting (exploratory code)
- `geonames/`: Fetching and managing Geoname data
- `hacks/`: Monkey patches and other hacks to fix bugs and get things working
- `images/`: Old-but-still-used images (that aren't part of the `assets/` setup)
- `loc/`: Location code (fetching from Google Maps API and Google Places API), caching, and some utility functions. Used by `servlets/`, so this should not itself contain servlet code.
- `logic/`: Catch-all directory for code that didn't make it into another top-level directory yet.
- `mail/`: Mails users
- `ml/`: Unused code, when I was exploring using a now-defunct Google Classifier API
- `nlp/`: Keyword-based classifier code
- `node_server/`: The JS server that runs in the cloud. Used for rendering server-side React (and compiling MJML to valid email)
- `notifications/`: Sends notifications to users (currently android-only)
- `profiles/`: Support basic user profile pages (super-old exploratory code)
- `pubsub/`: Posts to Twitter and FB. Both weekly schedules, per-event additions, filtering critera, etc
- `rankings/`: Rank cities by events and users, both calculation and display
- `search/`: The event search functionality, built on top of GAE Search. Used to support city, location, style searches. As well as exploratory code for Page searches (beyond Event searches)
- `services/`: Underlying services that we had to reimplement as we migrate of GAE Standard to GAE Flex
- `servlets/`: Catch-all directory for servlet rendering code that didn't make it into another top-level directory yet. Depends on `logic/`.
- `templates/`: Jinja2 templates used to render the site. Many of the more complex rendering has been moved into React JS rendering in `assets/`.
- `test_utils/`: Reusable utility code for tests
- `tools/`: Generic scripts (not needed by the webserver itself)
- `topics/`: Topic Pages, aka Dancer pages (exploratory code)
- `tutorials/`: Tutorials, display and rendering.
- `users/`: User code, for account management
- `util/`: Util code, should have minimal dependencies, and be unrelated to DanceDeets business logic
- `web_events/`: Web Events, distinct from FB Events, are events that come from scraped webpages. Primarily used for Korea and Japan.

Some important scripts:
- `setup.sh`: A script to initialize the machine, directory, and get everything ready for development and pushing.
- `setup.py`: A script to package up the project for use on ScrapingHub. So only contains a subset of the code, mostly `classes/` stuff and dependencies.
- `gulpfile.babel.js`: Has most of the commands and build logic for the site.
- `webpack.config.amp.babel.js`: Builds the AMP CSS (using Uncss), as a minified compressed CSS that can be inlined directly
- `webpack.config.client.babel.js`: Generates the client code (JS, CSS, Images) from `assets/`.
- `webpack.config.server.babel.js`: Generates the React templates as server JS code (packaged up for easy running within `node_server`)
