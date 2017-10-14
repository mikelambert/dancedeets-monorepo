/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import del from 'del';
import favicons from 'gulp-favicons';
import fetch from 'node-fetch';
import gutil from 'gutil';
import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import runSequence from 'run-sequence';
import { output as pagespeed } from 'psi';
import username from 'username';
import taskListing from 'gulp-task-listing';
import yargs from 'yargs';
import process from 'process';
import { generate as fontAwesomeGenerate } from 'font-awesome-svg-png/index';
// How bad is it to be importing from local files into our gulpfile?
// It means changes from the assets/ or dancedeets-common code now will sometimes require re-running gulp.
import { cdnBaseUrl } from '../common/js/util/url';
import exportedIcons from './assets/js/exportedIcons';

const argv = yargs
  .option('d', {
    alias: 'gae_dir',
    description: 'The directory containing dev_appserver.py',
    default: './frankenserver/python',
  })
  .help('h')
  .alias('h', 'help')
  .strict().argv;

gulp.task('help', taskListing);
gulp.task('default', taskListing);

const $ = gulpLoadPlugins();

const baseAssetsDir = `/Users/${username.sync()}/Dropbox/dancedeets-development/server/build-assets`;
const generatedFilesDir = `/Users/${username.sync()}/Dropbox/dancedeets-development/server/generated`;

// download the PR* data from GC Datastore, generate sqlite databases, and then upload them to GC Storage
gulp.task(
  'sqlite:generate',
  $.shell.task(['PYTHONPATH=. ./tools/download_pr_data.py'])
);
gulp.task(
  'sqlite:upload',
  $.shell.task(['PYTHONPATH=. ./tools/upload_pr_data.py'])
);

// TODO: Support login here, so that this URL can actually run. Currently blocked by 'login: admin'
gulp.task('web:events:resave', cb =>
  fetch(
    'https://www.dancedeets.com/tasks/reload_events?user_id=701004&allow_cache=1&disable_updates=regeocode,photo&queue=fast-queue&only_if_updated=0'
  ).then(x => console.log(x))
);

gulp.task(
  'compile:geonames:fetch_adgeolocs',
  $.shell.task(
    'PYTHONPATH=lib-local:lib-both:. python ./dancedeets/geonames/fetch_adgeolocs.py'
  )
);
gulp.task(
  'compile:geonames:build_cities_db',
  ['compile:geonames:fetch_adgeolocs'],
  $.shell.task(
    `PYTHONPATH=lib-local:lib-both:. python ./dancedeets/geonames/build_cities_db.py ${generatedFilesDir}/cities.db`
  )
);
gulp.task('compile:geonames', ['compile:geonames:build_cities_db']);

gulp.task(
  'compile:test-geonames:build_cities_db',
  $.shell.task(
    'PYTHONPATH=lib-local:lib-both:. DUMMY_FILE=1 python ./dancedeets/geonames/build_cities_db.py ./dancedeets/geonames/cities_test.db'
  )
);
gulp.task('compile:test-geonames', ['compile:test-geonames:build_cities_db']);

const faviconsFilename = './dist/templates/favicon_tags.html';
gulp.task(
  'compile:images:favicons:delete',
  $.shell.task(`rm -f ${faviconsFilename}`)
);
gulp.task('compile:images:favicons', ['compile:images:favicons:delete'], () =>
  gulp
    .src('assets/img/deets-head.png')
    .pipe(
      favicons({
        appName: 'DanceDeets',
        appDescription: 'Street Dance Events. Worldwide.',
        developerName: 'DanceDeets',
        developerURL: 'https://www.dancedeets.com/',
        background: '#fff',
        path: `${cdnBaseUrl}/img/favicons/`,
        url: 'https://www.dancedeets.com/',
        display: 'standalone',
        orientation: 'portrait',
        version: 1.0,
        logging: false,
        // Unfortunately, the online generator doesn't seem to include 'short_name' in manifest.json
        online: false,
        icons: {
          opengraph: false,
          twitter: false,
        },
        html: faviconsFilename,
        replace: true,
      })
    )
    .on('error', gutil.log)
    .pipe(gulp.dest('./dist/img/favicons/'))
);

gulp.task(
  'compile:manifest',
  ['compile:images:favicons'],
  $.shell.task('python ./tools/update_manifest.py')
);

// These are images we grab expanded versions from font-awesome, for uploading to the site.
// In particular, these are used by the mail we send out.
gulp.task('compile:images:font-awesome', cb =>
  fontAwesomeGenerate({
    color: 'black',
    png: true,
    sizes: [16],
    icons: exportedIcons,
    dest: 'dist/img/font-awesome/',
  })
);

gulp.task('compile:images:assets-to-dist', () =>
  gulp
    .src(`./assets/img/**/*.{png,jpg}`)
    .pipe(
      $.imagemin({
        progressive: true,
        interlaced: true,
      })
    )
    .pipe(gulp.dest('dist/img'))
);

gulp.task('compile:images:resize', () =>
  gulp
    .src(`${baseAssetsDir}/img/**/*.{png,jpg}`)
    .pipe(
      $.responsiveImages({
        'classes/*/*.*': [
          {
            width: 32,
            height: 32,
            format: 'png',
          },
        ],
        '{location,style}-*.jpg': [
          {
            width: 450,
            height: 300,
            crop: 'true',
            quality: 60,
          },
        ],
        'deets-activity-*.png': [
          {
            height: 100,
          },
        ],
        'background*.jpg': [
          {
            width: 1200,
            quality: 60,
            suffix: '@2x',
          },
          {
            width: 600,
            quality: 60,
          },
        ],
        'screenshot-*.jpg': [
          {
            format: 'jpg',
            quality: 60,
          },
        ],
        'deets-head-and-title-on-black.png': [
          {
            height: 64 * 2,
            suffix: '@2x',
          },
          {
            height: 64,
          },
          {
            height: 60,
            suffix: '-60px',
          },
        ],
        'fb-login.png': [{}],
      })
    )
    .pipe(
      $.imagemin({
        progressive: true,
        interlaced: true,
      })
    )
    .pipe(gulp.dest('dist/img'))
);

gulp.task('compile:images:shared-resize', () =>
  gulp
    .src(`../common/js/**/*.{png,jpg}`)
    .pipe(
      $.responsiveImages({
        'styles/images/*.png': [
          {
            width: 100,
            height: 100,
            format: 'png',
          },
        ],
      })
    )
    .pipe(
      $.imagemin({
        progressive: true,
        interlaced: true,
      })
    )
    .pipe(gulp.dest('dist/img'))
);
// gets deets-activity svg files
gulp.task('compile:images:svg', () =>
  gulp
    .src(`${baseAssetsDir}/img/*.svg`)
    .pipe(
      $.cache(
        $.imagemin({
          progressive: true,
          interlaced: true,
        })
      )
    )
    .pipe(gulp.dest('dist/img'))
);

gulp.task('compile:images', [
  'compile:images:favicons',
  'compile:images:font-awesome',
  'compile:images:assets-to-dist',
  'compile:images:resize',
  'compile:images:shared-resize',
  'compile:images:svg',
  'compile:manifest',
]);

gulp.task('compile:fonts', () =>
  gulp
    .src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'))
);

// Run PageSpeed Insights
gulp.task('pagespeed', cb =>
  // Update the below URL to the public URL of your site
  pagespeed(
    'https://www.dancedeets.com/new_homepage',
    {
      strategy: 'mobile',
      // By default we use the PageSpeed Insights free (no API key) tier.
      // Use a Google Developer API key if you have one: http://goo.gl/RkN0vE
      // key: 'YOUR_API_KEY'
    },
    cb
  )
);

gulp.task('deploy:cleanup-files', () =>
  del.sync('lib/setuptools/script (dev).tmpl')
);

gulp.task(
  'deploy:server:toofast',
  $.shell.task(['./build_tools/buildpush.sh'])
);
gulp.task(
  'deploy:memory_leak_server:generate_yaml',
  $.shell.task(['./build_tools/create_memory_service_yaml.sh'])
);
gulp.task(
  'deploy:memory_leak_server:toofast',
  ['deploy:memory_leak_server:generate_yaml'],
  $.shell.task(['./build_tools/buildpush_memory.sh'])
);
gulp.task(
  'deploy:server:prepush',
  $.shell.task(['./build_tools/check_for_native_modules.sh'])
);
gulp.task('deploy:server:fast', cb =>
  runSequence('deploy:server:prepush', 'deploy:server:toofast', cb)
);
gulp.task('deploy:server', cb =>
  runSequence('deploy:cleanup-files', 'compile', 'deploy:server:fast', cb)
);
gulp.task('deploy:memory_leak_server', cb =>
  runSequence('deploy:server:prepush', 'deploy:memory_leak_server:toofast', cb)
);

gulp.task('deploy', ['deploy:server', 'deploy:scrapy']);
gulp.task('deployServer', ['deploy:server']);
gulp.task('deployServerFast', ['deploy:server:fast']);
gulp.task('deployScrapy', ['deploy:scrapy']);

// If this fails due to google imports, make sure to delete site-packages/.../proto* modules
gulp.task(
  'generate-amp-sources',
  $.shell.task(['PYTHONPATH=lib-local:. ./amp/generate_amp_sources.py'])
);

function webpack(configName, dependencies = []) {
  const webpackCommand = `node_modules/webpack/bin/webpack.js --color --progress --config webpack.config.${configName}.babel.js`;
  gulp.task(
    `compile:webpack:${configName}:prod:once`,
    dependencies,
    // We must pass NODE_ENV here, because otherwise inside webpack, it's too late for babel plugins
    $.shell.task([`NODE_ENV=production ${webpackCommand}`])
  );
  gulp.task(
    `compile:webpack:${configName}:prod:watch`,
    dependencies,
    $.shell.task([`NODE_ENV=production ${webpackCommand} --watch`])
  );
  gulp.task(
    `compile:webpack:${configName}:debug:once`,
    dependencies,
    $.shell.task([`${webpackCommand} --debug`])
  );
  gulp.task(
    `compile:webpack:${configName}:debug:watch`,
    dependencies,
    $.shell.task([`${webpackCommand} --watch --debug`])
  );
  gulp.task(
    `compile:webpack:${configName}:json`,
    dependencies,
    $.shell.task([
      `${webpackCommand} --json > webpack-${configName}-output.json`,
    ])
  );
}
// Generate rules for our three webpack configs
webpack('server');
webpack('client');
// Fo rrunning uncss on a minimal amp page render
if (process.env.TRAVIS) {
  // We disable generate-amp-sources on Travis CI,
  // because it dies when trying to 'import webtest'.
  webpack('amp');
  // For running uncss on a full page render
  webpack('uncss');
} else {
  webpack('amp', ['generate-amp-sources']);
  // For running uncss on a full page render
  webpack('uncss', ['generate-amp-sources']);
}

const webpackConfigs = ['amp', 'server', 'client', 'uncss'];

const suffixes = ['prod:once', 'prod:watch', 'debug:once', 'debug:watch'];
suffixes.forEach(suffix =>
  gulp.task(
    `compile:webpack:all:${suffix}`,
    webpackConfigs.map(x => `compile:webpack:${x}:${suffix}`)
  )
);

gulp.task('compile:webpack', ['compile:webpack:all:prod:once']);
gulp.task('compile', [
  'compile:webpack',
  'compile:images',
  'compile:fonts',
  'compile:geonames',
]);

// When debugging webpack bundle sizes, we can use js:size:* here
// as well as track who references what, with http://webpack.github.io/analyse
['common', 'eventSearchResultsExec'].forEach(filename =>
  gulp.task(
    `js:size:${filename}`,
    $.shell.task(
      `./node_modules/source-map-explorer/index.js dist/js/${filename}.js{,.map}`
    )
  )
);

gulp.task('clean', () => del.sync('dist'));

gulp.task('test', $.shell.task(['./build_tools/test.sh']));

gulp.task('rebuild', cb => runSequence('clean', 'compile', 'test', cb));

gulp.task('datalab:setup', $.shell.task('gcloud components install datalab'));

gulp.task(
  'datalab:create',
  ['datalab:setup'],
  $.shell.task([`datalab create dl-${username.sync()} --disk-size-gb 1`])
);
gulp.task(
  'datalab:start',
  ['datalab:setup'],
  $.shell.task([`datalab connect dl-${username.sync()}`])
);
gulp.task(
  'datalab:stop',
  ['datalab:setup'],
  $.shell.task([`datalab stop dl-${username.sync()}`])
);

gulp.task(
  'dev-appserver:create-yaml:hot',
  $.shell.task(['HOT_SERVER_PORT=8080 ./build_tools/create_devserver_yaml.sh'])
);
gulp.task(
  'dev-appserver:create-yaml:regular',
  $.shell.task(['./build_tools/create_devserver_yaml.sh'])
);

gulp.task(
  'dev-appserver:wait-for-exit',
  $.shell.task(['./build_tools/wait_for_dev_appserver_exit.sh'])
);

const storagePath = '~/Documents/dancedeets-storage/';

gulp.task(
  'dev-appserver:create-storage-dir',
  $.shell.task([`mkdir -p ${storagePath}`])
);

function startDevAppServer(port) {
  return $.shell.task([
    `PYTHONPATH=lib-local ${argv.gae_dir}/dev_appserver.py app-devserver.yaml --port=${port} --runtime=python-compat --storage_path=${storagePath} 2>&1 | ~/Library/Python/2.7/bin/technicolor-yawn`,
  ]);
}
gulp.task(
  'dev-appserver:kill',
  $.shell.task(['./build_tools/force_kill_server.sh'])
);

gulp.task('dev-appserver:server:regular:force', cb =>
  runSequence('dev-appserver:kill', 'dev-appserver:server:regular', cb)
);
gulp.task('dev-appserver:server:hot:force', cb =>
  runSequence('dev-appserver:kill', 'dev-appserver:server:hot', cb)
);

['hot', 'regular'].forEach(x => {
  const port = x.includes('hot') ? 8085 : 8080;
  gulp.task(
    `dev-appserver:server:${x}`,
    [
      `dev-appserver:create-yaml:${x}`,
      'dev-appserver:wait-for-exit',
      'dev-appserver:create-storage-dir',
    ],
    startDevAppServer(port)
  );
  gulp.task(`dev-appserver:server:${x}:force`, cb =>
    runSequence('dev-appserver:kill', `dev-appserver:server:${x}`, cb)
  );
});

gulp.task(
  'react-server',
  $.shell.task(['../runNode.js ./node_server/renderServer.js --port 8090'])
);

const dockerImages = [
  'gae-py-js',
  'gae-nginx',
  'gae-geos',
  'gae-binaries',
  'gae-modules',
  'gae-modules-py',
];
dockerImages.forEach(imageName => {
  gulp.task(
    `buildDocker:one:${imageName}`,
    $.shell.task([`cd docker/${imageName} && ./build.sh`])
  );
});
dockerImages.forEach((imageName, index) => {
  const allFollowingImageNames = dockerImages.slice(index);
  gulp.task(`buildDocker:${imageName}`, cb =>
    runSequence(...allFollowingImageNames.map(x => `buildDocker:one:${x}`))
  );
});
gulp.task('buildDocker', [`buildDocker:${dockerImages[0]}`]);

gulp.task(
  'server:datastore:local',
  $.shell.task([
    'gcloud beta emulators datastore start --no-store-on-disk --consistency=1.0 --host-port=localhost:8095',
  ])
);

// Workable Dev Server (1): Hot reloading
// Port 8090: Backend React Render server
// (We don't really use this, but it's there in case our generate_amp_sources/compilation tasks want it)
gulp.task('server:hot:node', ['react-server']);
// Port 8085: Middle Python server.
gulp.task('server:hot:python', ['dev-appserver:server:hot']);
gulp.task('server:hot:python:force', ['dev-appserver:server:hot:force']);
// Port 8080: Frontend Javascript Server (Handles Hot Reloads and proxies the rest to Middle Python)
gulp.task(
  'server:hot:frontend',
  $.shell.task([
    '../runNode.js ./hotServer.js --debug --port 8080 --backend 8085',
  ])
);
// Or we can run them all with:
gulp.task('server:hot', [
  'server:hot:node',
  'server:hot:python',
  'server:hot:frontend',
]);
gulp.task('server:hot:force', [
  'server:hot:node',
  'server:hot:python:force',
  'server:hot:frontend',
]);

// Workable Dev Server (2) Prod-like JS/CSS setup
// Port 8090: Backend React Render server
gulp.task('server:full:node', ['react-server']);
// Port 8080: Frontend Python server
gulp.task('server:full:python', ['dev-appserver:server:regular']);
// Also need to run the three webpack servers:
//    'compile:webpack:amp:prod:watch'
//    'compile:webpack:server:prod:watch'
//    'compile:webpack:client:prod:watch'
// Or we can run them all with:
gulp.task('server:full', [
  'server:full:node',
  'server:full:python',
  'compile:webpack:server:prod:watch',
  'compile:webpack:client:prod:watch',
  'server:datastore:local',
]);
// TODO: We ignore 'compile:webpack:amp:prod:watch' because it will need a running server to run against, and timing that is hard.

gulp.task('serverFull', ['server:full']);
gulp.task('serverHot', ['server:hot']);
