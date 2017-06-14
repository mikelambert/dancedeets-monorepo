// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import del from 'del';
import favicons from 'gulp-favicons';
import fetch from 'node-fetch';
import fs from 'fs';
import glob from 'glob';
import gutil from 'gutil';
import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import osHomedir from 'os-homedir';
import runSequence from 'run-sequence';
import { output as pagespeed } from 'psi';
import username from 'username';
import taskListing from 'gulp-task-listing';
import yaml from 'js-yaml';
import yargs from 'yargs';
import process from 'process';
import childProcess from 'child_process';
import { generate as fontAwesomeGenerate } from 'font-awesome-svg-png/index';
// How bad is it to be importing from 'assets' into our gulpfile?
// It means changes from the assets/ dir now will sometimes require re-running gulp.
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

const baseAssetsDir = `/Users/${username.sync()}/Dropbox/dancedeets/art/build-assets/`;

// TODO: Support login here, so that this URL can actually run. Currently blocked by 'login: admin'
gulp.task('web:events:resave', cb =>
  fetch(
    'http://www.dancedeets.com/tasks/reload_events?user_id=701004&allow_cache=1&disable_updates=regeocode,photo&queue=fast-queue&only_if_updated=0'
  ).then(x => console.log(x))
);

gulp.task(
  'compile:geonames:fetch_adgeolocs',
  $.shell.task(
    'PYTHONPATH=lib-local:lib-both:. python ./geonames/fetch_adgeolocs.py'
  )
);
gulp.task(
  'compile:geonames:build_cities_db',
  ['compile:geonames:fetch_adgeolocs'],
  $.shell.task(
    'PYTHONPATH=lib-local:lib-both:. python ./geonames/build_cities_db.py ./geonames/cities.db'
  )
);
gulp.task('compile:geonames', ['compile:geonames:build_cities_db']);

gulp.task(
  'compile:test-geonames:build_cities_db',
  $.shell.task(
    'PYTHONPATH=lib-local:lib-both:. DUMMY_FILE=1 python ./geonames/build_cities_db.py ./geonames/cities_test.db'
  )
);
gulp.task('compile:test-geonames', ['compile:test-geonames:build_cities_db']);

gulp.task('compile:images:favicons', () =>
  gulp
    .src('assets/img/deets-head.png')
    .pipe(
      favicons({
        appName: 'DanceDeets',
        appDescription: 'Street Dance Events. Worldwide.',
        developerName: 'DanceDeets',
        developerURL: 'http://www.dancedeets.com/',
        background: '#fff',
        path: '/dist/img/favicons/',
        url: 'http://www.dancedeets.com/',
        display: 'standalone',
        orientation: 'portrait',
        version: 1.0,
        logging: false,
        online: true,
        icons: {
          opengraph: false,
          twitter: false,
        },
        html: './dist/templates/favicon_tags.html',
        replace: true,
      })
    )
    .on('error', gutil.log)
    .pipe(gulp.dest('./dist/img/favicons/'))
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
      $.responsiveImages({
        // We reference categories-black.png from our mails
        'categories-*.png': [{}],
      })
    )
    .pipe(gulp.dest('dist/img'))
);

gulp.task('compile:images:resize', () =>
  gulp
    .src(`${baseAssetsDir}img/**/*.{png,jpg}`)
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
    .src(`${baseAssetsDir}img/*.svg`)
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
    'http://www.dancedeets.com/new_homepage',
    {
      strategy: 'mobile',
      // By default we use the PageSpeed Insights free (no API key) tier.
      // Use a Google Developer API key if you have one: http://goo.gl/RkN0vE
      // key: 'YOUR_API_KEY'
    },
    cb
  )
);

function getScrapyNames(pattern) {
  return glob
    .sync(pattern)
    .map(filename => {
      const contents = fs.readFileSync(filename, 'utf8');
      const match = contents.match(/name = ['"](.*)['"]/);
      if (match) {
        return match[1];
      } else {
        return null;
      }
    })
    .filter(x => x);
}

const webEventNames = getScrapyNames('web_events/scraper/spiders/*.py');
const classesNames = getScrapyNames('classes/scraper/spiders/*.py');

webEventNames
  .concat(classesNames)
  .forEach(x =>
    gulp.task(`scrape:one:${x}`, $.shell.task(`./scrapy_bin.py crawl ${x}`))
  );
gulp.task('scrape:web:scrapy', webEventNames.map(x => `scrape:one:${x}`));
gulp.task('scrape:classes:scrapy', classesNames.map(x => `scrape:one:${x}`));
gulp.task(
  'scrape:classes:index:prod',
  $.shell.task(['curl http://www.dancedeets.com/classes/reindex'])
);
gulp.task(
  'scrape:classes:index:dev',
  $.shell.task(['curl http://dev.dancedeets.com:8080/classes/reindex'])
);
gulp.task('scrape:web', ['scrape:web:scrapy']);
gulp.task('scrape:classes', cb =>
  runSequence(
    'scrape:classes:scrapy',
    ['scrape:classes:index:prod', 'scrape:classes:index:dev'],
    cb
  )
);
gulp.task('scrapeWeb', ['scrape:web']);
gulp.task('scrapeClasses', ['scrape:classes']);

function getScrapyKey() {
  if (!fs.existsSync('keys.yaml')) {
    return 'NO KEY';
  }
  const yamlDoc = yaml.safeLoad(fs.readFileSync('keys.yaml', 'utf8'));
  return yamlDoc.scrapinghub_key;
}

gulp.task(
  'deploy:scrapy',
  $.shell.task([`echo ${getScrapyKey()} | shub login`, 'shub deploy'])
);
gulp.task('deploy:cleanup-files', () =>
  del.sync('lib/setuptools/script (dev).tmpl')
);

function executeCommand(command) {
  return new Promise((resolve, reject) => {
    const ls = childProcess.spawn('sh', ['-c', command], {
      stdio: ['inherit', 'inherit', 'inherit'],
    });

    ls.on('error', reject);
    ls.on('exit', code => {
      if (code === 0) {
        resolve();
      } else {
        reject(code);
      }
    });
  });
}

gulp.task('deploy:server:toofast', $.shell.task(['./buildpush.sh']));
gulp.task(
  'deploy:memory_leak_server:generate_yaml',
  $.shell.task(['./create_memory_service_yaml.sh'])
);
gulp.task(
  'deploy:memory_leak_server:toofast',
  ['deploy:memory_leak_server:generate_yaml'],
  $.shell.task(['./buildpush_memory.sh'])
);
gulp.task(
  'deploy:server:prepush',
  $.shell.task(['./tools/check_for_native_modules.sh'])
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
  $.shell.task(['./amp/generate_amp_sources.py'])
);

function webpack(configName, dependencies = []) {
  const webpackCommand = `node_modules/webpack/bin/webpack.js --color --progress --config webpack.config.${configName}.babel.js`;
  gulp.task(
    `compile:webpack:${configName}:prod:once`,
    dependencies,
    $.shell.task([webpackCommand])
  );
  gulp.task(
    `compile:webpack:${configName}:prod:watch`,
    dependencies,
    $.shell.task([`${webpackCommand} --watch`])
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
}
// Generate rules for our three webpack configs
webpack('server');
webpack('client');
if (process.env.TRAVIS) {
  // We disable generate-amp-sources on Travis CI,
  // because it dies when trying to 'import webtest'.
  webpack('amp');
} else {
  webpack('amp', ['generate-amp-sources']);
}

const webpackConfigs = ['amp', 'server', 'client'];

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

gulp.task('clean', () => del.sync('dist'));

gulp.task('test', $.shell.task(['./test.sh']));

gulp.task('rebuild', cb => runSequence('clean', 'compile', 'test', cb));

const homedir = osHomedir();
gulp.task(
  'datalab:local',
  $.shell.task([
    `docker run -it -p "127.0.0.1:8081:8080" -v "${homedir}:/content" -e "PROJECT_ID=dancedeets-hrd" gcr.io/cloud-datalab/datalab:local`,
  ])
);
gulp.task('datalab:remote:start', $.shell.task([`datalab connect dl`]));
gulp.task('datalab:remote:stop', $.shell.task([`datalab stop dl`]));

gulp.task(
  'dev-appserver:create-yaml:hot',
  $.shell.task(['HOT_SERVER_PORT=8080 ./create_devserver_yaml.sh'])
);
gulp.task(
  'dev-appserver:create-yaml:regular',
  $.shell.task(['./create_devserver_yaml.sh'])
);

gulp.task(
  'dev-appserver:wait-for-exit',
  $.shell.task(['./wait_for_dev_appserver_exit.sh'])
);

function startDevAppServer(port) {
  return $.shell.task([
    `PYTHONPATH=lib-local ${argv.gae_dir}/dev_appserver.py app-devserver.yaml --port=${port} --runtime=python-compat --storage_path=~/Projects/dancedeets-storage/ 2>&1 | technicolor-yawn`,
  ]);
}
gulp.task('dev-appserver:kill', $.shell.task(['./force_kill_server.sh']));

gulp.task(
  'dev-appserver:server:regular',
  ['dev-appserver:create-yaml:regular', 'dev-appserver:wait-for-exit'],
  startDevAppServer(8080)
);
gulp.task(
  'dev-appserver:server:hot',
  ['dev-appserver:create-yaml:hot', 'dev-appserver:wait-for-exit'],
  startDevAppServer(8085)
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
    [`dev-appserver:create-yaml:${x}`, 'dev-appserver:wait-for-exit'],
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
