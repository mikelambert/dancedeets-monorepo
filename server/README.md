[![Build Status](https://travis-ci.org/mikelambert/dancedeets-monorepo.svg?branch=master)](https://travis-ci.org/mikelambert/dancedeets-monorepo)

[![Coveralls](https://coveralls.io/repos/mikelambert/dancedeets/badge.svg?branch=master&service=github)](https://coveralls.io/github/mikelambert/dancedeets?branch=master)

# DanceDeets

The magic behind <https://www.dancedeets.com/>.

## Setup

First, download and install appengine libraries here:
<https://developers.google.com/appengine/downloads>
...and open the AppEngine app at least once, to set up `/usr/local/google_appengine`.

Second, setup gcloud:
```
curl https://sdk.cloud.google.com | bash
gcloud components update app preview
gcloud config set project dancedeets-hrd
gcloud auth login
gcloud app run app.yaml
```

Third, to setup dancedeets, run `./setup.sh`. It will download and install libraries,
and setup some in our `lib/` directory for uploading to appengine.

You can run a variety of commands from gulp:
- `gulp test` to run all of the included tests.
- `gulp server:hot` to run a local server
- `gulp deployServer` to push to production

If you are running the NLP classifier evaluations, you may want to setup re2 for speed.
To do this, download/install from <https://github.com/google/re2/>
Then install `pip install re2` to get the python wrappers.

## Code Layout

- [`assets/`](assets): The Frontend code, used by Webpack to build out the JS, CSS, and Images (written into [`dist/`](dist))
- [`amp/`](amp): Google AMP support tools
- [`brackets/`](brackets): Show youtube videos in a nice battle display format (exploratory code)
- [`battle_brackets/`](battle_brackets): Handle the server-side of the Battle Brackets I was building on mobile (exploratory code)
- [`classes/`](classes): Scrape and display the Class schedules in LA and NYC
- [`classifiers/`](classifiers): Help tune and tweak the keyword-based classifier. Not worth worrying about unless making changes there
- [`docker/`](docker): The docker images used by our project (Should set these up using [`gulpfile.babel.js`](gulpfile.babel.js))
- [`event_attendees/`](event_attendees): The attendee-based event classifier
- [`event_scraper/`](event_scraper): Scrapes the FB pages/groups, as well as the signed-in users' events, to find and classify events
- [`events/`](events): Event code (locations, reloading, adding/removing, images, etc). Everything not classifier/scraping-related.
- [`favorites/`](favorites): First attempt at setting up event-favoriting (exploratory code)
- [`geonames/`](geonames): Fetching and managing Geoname data
- [`hacks/`](hacks): Monkey patches and other hacks to fix bugs and get things working
- [`images/`](images): Old-but-still-used images (that aren't part of the [`assets/`](assets) setup)
- [`loc/`](loc): Location code (fetching from Google Maps API and Google Places API), caching, and some utility functions. Used by [`servlets/`](servlets), so this should not itself contain servlet code.
- [`logic/`](logic): Catch-all directory for code that didn't make it into another top-level directory yet.
- [`mail/`](mail): Mails users
- [`ml/`](ml): Unused code, when I was exploring using a now-defunct Google Classifier API
- [`nlp/`](nlp): Keyword-based classifier code
- [`node_server/`](node_server): The JS server that runs in the cloud. Used for rendering server-side React (and compiling MJML to valid email)
- [`notifications/`](notifications): Sends notifications to users (currently android-only)
- [`profiles/`](profiles): Support basic user profile pages (super-old exploratory code)
- [`pubsub/`](pubsub): Posts to Twitter and FB. Both weekly schedules, per-event additions, filtering critera, etc
- [`rankings/`](rankings): Rank cities by events and users, both calculation and display
- [`search/`](search): The event search functionality, built on top of GAE Search. Used to support city, location, style searches. As well as exploratory code for Page searches (beyond Event searches)
- [`services/`](services): Underlying services that we had to reimplement as we migrate of GAE Standard to GAE Flex
- [`servlets/`](servlets): Catch-all directory for servlet rendering code that didn't make it into another top-level directory yet. Depends on [`logic/`](logic).
- [`templates/`](templates): Jinja2 templates used to render the site. Many of the more complex rendering has been moved into React JS rendering in [`assets/`](assets).
- [`test_utils/`](test_utils): Reusable utility code for tests
- [`tools/`](tools): Generic scripts (not needed by the webserver itself)
- [`topics/`](topics): Topic Pages, aka Dancer pages (exploratory code)
- [`tutorials/`](tutorials): Tutorials, display and rendering.
- [`users/`](users): User code, for account management
- [`util/`](util): Util code, should have minimal dependencies, and be unrelated to DanceDeets business logic
- [`web_events/`](web_events): Web Events, distinct from FB Events, are events that come from scraped webpages. Primarily used for Korea and Japan.

Some important scripts:
- [`setup.sh`](setup.sh): A script to initialize the machine, directory, and get everything ready for development and pushing.
- [`setup.py`](setup.py): A script to package up the project for use on ScrapingHub. So only contains a subset of the code, mostly [`classes/`](classes/) stuff and dependencies.
- [`gulpfile.babel.js`](gulpfile.babel.js): Has most of the commands and build logic for the site.
- [`webpack.config.amp.babel.js`](webpack.config.amp.babel.js): Builds the AMP CSS (using Uncss), as a minified compressed CSS that can be inlined directly
- [`webpack.config.client.babel.js`](webpack.config.client.babel.js): Generates the client code (JS, CSS, Images) from [`assets/`](assets/).
- [`webpack.config.server.babel.js`](webpack.config.server.babel.js): Generates the React templates as server JS code (packaged up for easy running within [`node_server`](node_server))
