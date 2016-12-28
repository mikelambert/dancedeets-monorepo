
// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import del from 'del';
import favicons from 'gulp-favicons';
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

const argv = yargs
  .option('d', {
    alias: 'gae_dir',
    description: 'The directory containing dev_appserver.py',
    default: `${osHomedir()}/google-cloud-sdk/bin`,
  })
  .help('h').alias('h', 'help')
  .strict()
  .argv;

gulp.task('help', taskListing);
gulp.task('default', taskListing);

const $ = gulpLoadPlugins();

const baseAssetsDir = `/Users/${username.sync()}/Dropbox/dancedeets/art/build-assets/`;

gulp.task('compile:images:favicons', () => gulp
  .src('assets/img/deets-head.png')
  .pipe(favicons({
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
  }))
  .on('error', gutil.log)
  .pipe(gulp.dest('./dist/img/favicons/'))
);

gulp.task('compile:images:resize', () => gulp
  .src(`${baseAssetsDir}img/**/*.{png,jpg}`)
  .pipe($.responsiveImages({
    'classes/*/*.*': [{
      width: 32,
      height: 32,
      format: 'png',
    }],
    '{location,style}-*.jpg': [{
      width: 450,
      height: 300,
      crop: 'true',
      quality: 60,
    }],
    'deets-activity-*.png': [{
      height: 100,
    }],
    'background*.jpg': [{
      width: 1200,
      quality: 60,
      suffix: '@2x',
    }, {
      width: 600,
      quality: 60,
    }],
    'screenshot-*.jpg': [{
      format: 'jpg',
      quality: 60,
    }],
    'deets-head-and-title-on-black.png': [{
      height: 64 * 2,
      suffix: '@2x',
    }, {
      height: 64,
    }, {
      height: 60,
      suffix: '-60px',
    }],
    'fb-login.png': [
    {},
    ],
  }))
  .pipe($.imagemin({
    progressive: true,
    interlaced: true,
  }))
  .pipe(gulp.dest('dist/img'))
);


gulp.task('compile:images:shared-resize', () => gulp
  .src(`../common/js/**/*.{png,jpg}`)
  .pipe($.responsiveImages({
    'styles/images/*.png': [{
      width: 100,
      height: 100,
      format: 'png',
      }],
  }))
  .pipe($.imagemin({
    progressive: true,
    interlaced: true,
  }))
  .pipe(gulp.dest('dist/img'))
);
// gets deets-activity svg files
gulp.task('compile:images:svg', () => gulp
  .src(`${baseAssetsDir}img/*.svg`)
  .pipe($.cache($.imagemin({
    progressive: true,
    interlaced: true,
  })))
  .pipe(gulp.dest('dist/img'))
);

gulp.task('compile:images', ['compile:images:favicons', 'compile:images:resize', 'compile:images:shared-resize', 'compile:images:svg']);

gulp.task('compile:fonts', () => gulp
  .src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'))
);



// Run PageSpeed Insights
gulp.task('pagespeed', cb =>
  // Update the below URL to the public URL of your site
  pagespeed('http://www.dancedeets.com/new_homepage', {
    strategy: 'mobile',
    // By default we use the PageSpeed Insights free (no API key) tier.
    // Use a Google Developer API key if you have one: http://goo.gl/RkN0vE
    // key: 'YOUR_API_KEY'
  }, cb)
);


function getScrapyNames(pattern) {
  return glob.sync(pattern).map(filename => {
    const contents = fs.readFileSync(filename, 'utf8');
    const match = contents.match(/name = ['"](.*)['"]/);
    if (match) {
      return match[1];
    } else {
      return null;
    }
  }).filter(x => x);
}

const webEventNames = getScrapyNames('web_events/scraper/spiders/*.py');
const classesNames = getScrapyNames('classes/scraper/spiders/*.py');

webEventNames.concat(classesNames).forEach(x =>
  gulp.task(`scrape:one:${x}`, $.shell.task(`PYTHONPATH=/Library/Python/2.7/site-packages:$PYTHONPATH scrapy crawl ${x}`)));
gulp.task('scrape:web:scrapy',    webEventNames.map(x => `scrape:one:${x}`));
gulp.task('scrape:classes:scrapy', classesNames.map(x => `scrape:one:${x}`));
gulp.task('scrape:classes:index:prod', $.shell.task(['curl http://www.dancedeets.com/classes/reindex']))
gulp.task('scrape:classes:index:dev',  $.shell.task(['curl http://dev.dancedeets.com:8080/classes/reindex']))
gulp.task('scrape:web', ['scrape:web:scrapy']);
gulp.task('scrape:classes', cb => runSequence('scrape:classes:scrapy', ['scrape:classes:index:prod', 'scrape:classes:index:dev'], cb));
gulp.task('scrapeWeb', ['scrape:web']);
gulp.task('scrapeClasses', ['scrape:classes']);

function getScrapyKey() {
  if (!fs.existsSync('keys.yaml')) {
    return 'NO KEY';
  }
  const yamlDoc = yaml.safeLoad(fs.readFileSync('keys.yaml', 'utf8'))
  return yamlDoc.scrapinghub_key
}

gulp.task('deploy:scrapy', $.shell.task([
  `echo ${getScrapyKey()} | shub login`,
  'shub deploy',
]));
gulp.task('deploy:cleanup-files', () => del.sync('lib/setuptools/script (dev).tmpl'))

gulp.task('deploy:server:fast', $.shell.task(['gcloud app deploy app.yaml --quiet']));
gulp.task('deploy:server', cb => runSequence('deploy:cleanup-files', 'compile', 'deploy:server:fast', cb));

gulp.task('deploy', ['deploy:server', 'deploy:scrapy']);
gulp.task('deployServer', ['deploy:server'])
gulp.task('deployServerFast', ['deploy:server:fast'])
gulp.task('deployScrapy', ['deploy:scrapy'])

// TODO: This was erroring out due to a mysterious 'google' module that I can't eliminate.
// So I'm silencing it with '|| true' for now, so I can continue to push.
gulp.task('generate-amp-sources', $.shell.task(['./amp/generate_amp_sources.py || true']));

function webpack(configName, dependencies = []) {
  const webpackCommand = `node_modules/webpack/bin/webpack.js --color --progress --config webpack.config.${configName}.babel.js`;
  gulp.task(`compile:webpack:${configName}:prod:once`, dependencies, $.shell.task([webpackCommand]));
  gulp.task(`compile:webpack:${configName}:prod:watch`, dependencies, $.shell.task([`${webpackCommand} --watch`]));
  gulp.task(`compile:webpack:${configName}:debug:once`, dependencies, $.shell.task([`${webpackCommand} --debug`]));
  gulp.task(`compile:webpack:${configName}:debug:watch`, dependencies, $.shell.task([`${webpackCommand} --watch --debug`]));
}
// Generate rules for our three webpack configs
webpack('amp', ['generate-amp-sources']);
webpack('server');
webpack('client');

const webpackConfigs = ['amp', 'server', 'client'];

const suffixes = ['prod:once', 'prod:watch', 'debug:once', 'debug:watch'];
suffixes.forEach(suffix =>
  gulp.task(`compile:webpack:all:${suffix}`, webpackConfigs.map(x => `compile:webpack:${x}:${suffix}`))
);

gulp.task('compile:webpack', ['compile:webpack:all:prod:once'])
gulp.task('compile', ['compile:webpack', 'compile:images', 'compile:fonts']);

gulp.task('clean', () => del.sync('dist'));

gulp.task('test', $.shell.task(['./nose.sh']));

gulp.task('rebuild', cb => runSequence('clean', 'compile', 'test', cb));



gulp.task('datalab:start', $.shell.task(['gcloud app modules start datalab --version main']));
gulp.task('datalab:stop',  $.shell.task(['gcloud app modules stop  datalab --version main']));
gulp.task('datalab', ['datalab:start']);



gulp.task('dev-appserver:create-yaml:hot', $.shell.task(['HOT_SERVER_PORT=8080 ./create_devserver_yaml.sh']));
gulp.task('dev-appserver:create-yaml:regular', $.shell.task(['./create_devserver_yaml.sh']));

gulp.task('dev-appserver:wait-for-exit', $.shell.task(['./wait_for_dev_appserver_exit.sh']));

function startDevAppServer(port) {
  return () => gulp.src('app-devserver.yaml')
    .pipe($.gaeImproved('dev_appserver.py', {
      port: port,
      gae_dir: argv.gae_dir,
      storage_path: '~/Projects/dancedeets-storage/',
      runtime: 'python-compat',
    }));
}
gulp.task('dev-appserver:kill', $.shell.task(['./force_kill_server.sh']));

gulp.task('dev-appserver:server:regular', ['dev-appserver:create-yaml:regular', 'dev-appserver:wait-for-exit'], startDevAppServer(8080));
gulp.task('dev-appserver:server:hot',     ['dev-appserver:create-yaml:hot',     'dev-appserver:wait-for-exit'], startDevAppServer(8085));
gulp.task('dev-appserver:server:regular:force', cb => runSequence('dev-appserver:kill', 'dev-appserver:server:regular', cb));
gulp.task('dev-appserver:server:hot:force',     cb => runSequence('dev-appserver:kill', 'dev-appserver:server:hot', cb));

gulp.task('react-server', $.shell.task(['../runNode.js ./node_server/renderServer.js --port 8090']));


// Workable Dev Server (1): Hot reloading
// Port 8090: Backend React Render server
// (We don't really use this, but it's there in case our generate_amp_sources/compilation tasks want it)
gulp.task('server:hot:react', ['react-server']);
// Port 8085: Middle Python server.
gulp.task('server:hot:python', ['dev-appserver:server:hot']);
// Port 8080: Frontend Javascript Server (Handles Hot Reloads and proxies the rest to Middle Python)
gulp.task('server:hot:javascript', $.shell.task(['../runNode.js ./hotServer.js --debug --port 8080 --backend 8085']));
// Or we can run them all with:
gulp.task('server:hot', ['server:hot:react', 'server:hot:python', 'server:hot:javascript']);


// Workable Dev Server (2) Prod-like JS/CSS setup
// Port 8090: Backend React Render server
gulp.task('server:full:react', ['react-server']);
// Port 8080: Frontend Python server
gulp.task('server:full:python', ['dev-appserver:server:regular']);
// Also need to run the three webpack servers:
//    'compile:webpack:amp:prod:watch'
//    'compile:webpack:server:prod:watch'
//    'compile:webpack:client:prod:watch'
// Or we can run them all with:
gulp.task('server:full', ['server:full:react', 'server:full:python', 'compile:webpack:server:prod:watch', 'compile:webpack:client:prod:watch']);
// TODO: We ignore 'compile:webpack:amp:prod:watch' because it will need a running server to run against, and timing that is hard.

gulp.task('serverFull', ['server:full'])
gulp.task('serverHot', ['server:hot'])
