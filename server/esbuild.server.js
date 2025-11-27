/**
 * esbuild configuration for server-side bundles
 * Replaces webpack.config.server.babel.js
 *
 * Usage: node esbuild.server.js [--watch]
 */

const esbuild = require('esbuild');
const path = require('path');
const flowPlugin = require('esbuild-plugin-flow');

const isWatch = process.argv.includes('--watch');
const isProd = process.env.NODE_ENV === 'production' || !process.argv.includes('--debug');

// Entry points from the original webpack config
const entryPoints = {
  brackets: './assets/js/brackets.js',
  calendar: './assets/js/calendar.js',
  classResults: './assets/js/classResults.js',
  event: './assets/js/event.js',
  eventSearchResults: './assets/js/eventSearchResults.js',
  homepageReact: './assets/js/homepageReact.js',
  mailAddEvent: './assets/js/mailAddEvent.js',
  mailWeeklyNew: './assets/js/mailWeeklyNew.js',
  mailNewUser: './assets/js/mailNewUser.js',
  renderServer: './node_server/renderServer.js',
  topic: './assets/js/topic.js',
  tutorial: './assets/js/tutorial.js',
  tutorialCategory: './assets/js/tutorialCategory.js',
  weeklyMail: './assets/js/weeklyMail.js',
};

const buildOptions = {
  entryPoints: Object.values(entryPoints),
  entryNames: '[name]',
  bundle: true,
  platform: 'node',
  target: 'node20',
  outdir: path.join(__dirname, 'dist/js-server'),
  format: 'cjs', // CommonJS for compatibility with eval() in renderServer
  sourcemap: isProd ? 'external' : 'inline',
  minify: isProd,
  // Define process.env.NODE_ENV for React production builds
  define: {
    'process.env.NODE_ENV': JSON.stringify(isProd ? 'production' : 'development'),
  },
  // Handle CSS/images - ignore them for server builds (like null-loader)
  loader: {
    '.css': 'empty',
    '.scss': 'empty',
    '.sass': 'empty',
    '.png': 'empty',
    '.gif': 'empty',
    '.jpg': 'empty',
    '.jpeg': 'empty',
    '.svg': 'empty',
    '.ttf': 'empty',
    '.otf': 'empty',
    '.eot': 'empty',
    '.woff': 'empty',
    '.woff2': 'empty',
  },
  // Log build info
  logLevel: 'info',
  // mjml must be external - it has dynamic requires that can't be bundled
  // It will be loaded from node_modules at runtime
  external: ['mjml'],
  // Plugin to strip Flow type annotations
  plugins: [
    flowPlugin(/\.(js|jsx)$/, { all: true }),
  ],
};

async function build() {
  try {
    if (isWatch) {
      const ctx = await esbuild.context(buildOptions);
      await ctx.watch();
      console.log('Watching for changes...');
    } else {
      const start = Date.now();
      await esbuild.build(buildOptions);
      console.log(`Build completed in ${Date.now() - start}ms`);
    }
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();
