/**
 * esbuild configuration for client-side bundles
 * Replacement for webpack.config.client.js
 *
 * Usage:
 *   node esbuild.client.js           # Production build
 *   node esbuild.client.js --debug   # Development build
 *   NODE_ENV=production node esbuild.client.js  # Explicit production
 *
 * Output:
 *   - JS bundles: dist/js-esbuild/
 *   - CSS bundles: dist/css-esbuild/
 *   - Manifest: dist/manifest-esbuild.json (production only)
 *
 * Key differences from webpack.config.client.js:
 *   - No CommonsChunkPlugin code splitting (each entry gets full bundle)
 *   - No moment.js locale optimization (all locales included)
 *   - Uses native browser URL API polyfill instead of Node's url module
 *   - Watch mode not yet implemented (use webpack for dev)
 *
 * To switch from webpack to esbuild:
 *   1. Update server templates to load from js-esbuild/ and css-esbuild/
 *   2. Update manifest loading to use manifest-esbuild.json
 *   3. Test all client-side functionality
 */

const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');
const flowPlugin = require('esbuild-plugin-flow');
const sass = require('sass');
const crypto = require('crypto');

const isWatch = process.argv.includes('--watch');
const isProd = process.env.NODE_ENV === 'production' || !process.argv.includes('--debug');

// Entry points from webpack.config.client.js
const entryPoints = {
  addEvent: './assets/js/addEvent.js',
  bracketsExec: './assets/js/bracketsExec.js',
  calendarExec: './assets/js/calendarExec.js',
  homepageReact: './assets/js/homepageReactExec.js',
  homepage: './assets/js/homepage.js',
  normalPage: './assets/js/normalPage.js',
  classResultsExec: './assets/js/classResultsExec.js',
  eventExec: './assets/js/eventExec.js',
  eventSearchResultsExec: './assets/js/eventSearchResultsExec.js',
  topicExec: './assets/js/topicExec.js',
  tutorialExec: './assets/js/tutorialExec.js',
  tutorialCategoryExec: './assets/js/tutorialCategoryExec.js',
};

// Directories
const distDir = path.join(__dirname, 'dist');
const jsDir = path.join(distDir, 'js-esbuild');
const cssDir = path.join(distDir, 'css-esbuild');
const imgDir = path.join(distDir, 'img');
const fontsDir = path.join(distDir, 'fonts');

// Ensure output directories exist
[jsDir, cssDir, imgDir, fontsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Track CSS content per entry point for extraction (keyed by entry file path)
const cssContentsByPath = new Map();

// Track all assets for manifest generation
const assetManifest = {};

/**
 * Clean output directories before build
 */
function cleanOutputDirs() {
  [jsDir, cssDir].forEach(dir => {
    if (fs.existsSync(dir)) {
      fs.readdirSync(dir).forEach(file => {
        fs.unlinkSync(path.join(dir, file));
      });
    }
  });
}

/**
 * Generate a content hash for cache busting
 */
function contentHash(content) {
  return crypto.createHash('md5').update(content).digest('hex').slice(0, 20);
}

/**
 * Custom Sass importer to handle ~ prefix for node_modules
 */
function createTildeImporter(nodePaths) {
  return {
    findFileUrl(url) {
      if (!url.startsWith('~')) {
        return null;
      }
      // Remove ~ prefix and resolve from node_modules
      const modulePath = url.slice(1);
      for (const basePath of nodePaths) {
        const fullPath = path.join(basePath, modulePath);
        // Try with various extensions
        const extensions = ['', '.scss', '.sass', '.css'];
        for (const ext of extensions) {
          const testPath = fullPath + ext;
          if (fs.existsSync(testPath)) {
            return new URL('file://' + testPath);
          }
          // Also try _partial naming convention
          const dir = path.dirname(testPath);
          const file = path.basename(testPath);
          const partialPath = path.join(dir, '_' + file);
          if (fs.existsSync(partialPath)) {
            return new URL('file://' + partialPath);
          }
        }
      }
      return null;
    }
  };
}

/**
 * Custom plugin to handle SCSS/CSS files
 * Compiles SCSS to CSS and extracts to separate files
 */
const sassPlugin = {
  name: 'sass-plugin',
  setup(build) {
    // Handle .scss and .css imports
    build.onResolve({ filter: /\.s?css$/ }, args => {
      // Handle ~ prefix for node_modules
      let importPath = args.path;
      if (importPath.startsWith('~')) {
        importPath = importPath.slice(1);
      }

      // Try to resolve the path
      const resolveOptions = {
        paths: [
          args.resolveDir,
          path.join(__dirname, 'node_modules'),
          path.join(__dirname, '..', 'common', 'node_modules'),
        ],
      };

      try {
        let resolved;
        if (path.isAbsolute(importPath)) {
          resolved = importPath;
        } else if (importPath.startsWith('.')) {
          resolved = path.resolve(args.resolveDir, importPath);
        } else {
          // It's a node_modules import
          resolved = require.resolve(importPath, resolveOptions);
        }
        return { path: resolved, namespace: 'sass' };
      } catch (e) {
        // Try with .scss extension
        try {
          const resolved = require.resolve(importPath + '.scss', resolveOptions);
          return { path: resolved, namespace: 'sass' };
        } catch (e2) {
          return { path: args.path, namespace: 'sass' };
        }
      }
    });

    build.onLoad({ filter: /.*/, namespace: 'sass' }, async args => {
      try {
        const nodePaths = [
          path.join(__dirname, 'node_modules'),
        ];

        const result = sass.compile(args.path, {
          loadPaths: [
            path.dirname(args.path),
            path.join(__dirname, 'node_modules'),
            path.join(__dirname, 'assets', 'css'),
          ],
          importers: [createTildeImporter(nodePaths)],
          sourceMap: true,
          style: isProd ? 'compressed' : 'expanded',
          // Silence various deprecation warnings from third-party SCSS
          silenceDeprecations: ['import', 'global-builtin', 'color-functions', 'slash-div'],
        });

        // Store CSS content for later extraction (keyed by entry file path)
        const entryPath = build.initialOptions.entryPoints[0];
        if (!cssContentsByPath.has(entryPath)) {
          cssContentsByPath.set(entryPath, []);
        }
        cssContentsByPath.get(entryPath).push(result.css);

        // Return empty JS - CSS will be extracted separately
        return {
          contents: '',
          loader: 'js',
        };
      } catch (error) {
        return {
          errors: [{
            text: error.message,
            location: { file: args.path },
          }],
        };
      }
    });
  },
};

/**
 * Plugin to handle image files
 * Small images (< 10KB) are inlined as data URLs
 * Larger images are copied to dist/img
 */
const imagePlugin = {
  name: 'image-plugin',
  setup(build) {
    build.onResolve({ filter: /\.(png|gif|jpg|jpeg)$/ }, args => {
      let importPath = args.path;
      if (importPath.startsWith('~')) {
        importPath = importPath.slice(1);
      }

      try {
        let resolved;
        if (path.isAbsolute(importPath)) {
          resolved = importPath;
        } else if (importPath.startsWith('.')) {
          resolved = path.resolve(args.resolveDir, importPath);
        } else {
          resolved = require.resolve(importPath, {
            paths: [args.resolveDir, path.join(__dirname, 'node_modules')],
          });
        }
        return { path: resolved, namespace: 'image' };
      } catch (e) {
        return null;
      }
    });

    build.onLoad({ filter: /.*/, namespace: 'image' }, async args => {
      const content = fs.readFileSync(args.path);
      const ext = path.extname(args.path).slice(1);
      const name = path.basename(args.path);

      // Inline small images as data URLs (< 10KB like url-loader)
      if (content.length < 10000) {
        const mimeTypes = {
          png: 'image/png',
          gif: 'image/gif',
          jpg: 'image/jpeg',
          jpeg: 'image/jpeg',
        };
        const dataUrl = `data:${mimeTypes[ext]};base64,${content.toString('base64')}`;
        return {
          contents: `export default ${JSON.stringify(dataUrl)}`,
          loader: 'js',
        };
      }

      // Copy larger images to dist/img
      const destPath = path.join(imgDir, name);
      fs.copyFileSync(args.path, destPath);

      return {
        contents: `export default ${JSON.stringify('../img/' + name)}`,
        loader: 'js',
      };
    });
  },
};

/**
 * Plugin to handle font files
 */
const fontPlugin = {
  name: 'font-plugin',
  setup(build) {
    build.onResolve({ filter: /\.(ttf|otf|eot|svg|woff|woff2)(\?.*)?$/ }, args => {
      let importPath = args.path.split('?')[0]; // Remove query string
      if (importPath.startsWith('~')) {
        importPath = importPath.slice(1);
      }

      try {
        let resolved;
        if (path.isAbsolute(importPath)) {
          resolved = importPath;
        } else if (importPath.startsWith('.')) {
          resolved = path.resolve(args.resolveDir, importPath);
        } else {
          resolved = require.resolve(importPath, {
            paths: [args.resolveDir, path.join(__dirname, 'node_modules')],
          });
        }
        return { path: resolved, namespace: 'font' };
      } catch (e) {
        return null;
      }
    });

    build.onLoad({ filter: /.*/, namespace: 'font' }, async args => {
      const name = path.basename(args.path);
      const destPath = path.join(fontsDir, name);

      // Copy font to dist/fonts
      fs.copyFileSync(args.path, destPath);

      return {
        contents: `export default ${JSON.stringify('../fonts/' + name)}`,
        loader: 'js',
      };
    });
  },
};

/**
 * Build each entry point separately to enable CSS extraction per entry
 */
async function buildEntry(name, entryPath) {
  const outputName = isProd ? `${name}.[hash]` : name;

  const result = await esbuild.build({
    entryPoints: [entryPath],
    bundle: true,
    platform: 'browser',
    target: ['es2015'],
    outdir: jsDir,
    entryNames: outputName,
    format: 'iife',
    sourcemap: isProd ? 'external' : 'inline',
    minify: isProd,
    metafile: true,
    define: {
      'process.env.NODE_ENV': JSON.stringify(isProd ? 'production' : 'development'),
      'process.env.REACT_SPINKIT_NO_STYLES': JSON.stringify(true),
      'process.env.BROWSER': JSON.stringify(true),
      // Provide global for some modules that check for it
      'global': 'window',
    },
    // Provide fetch polyfill globally
    inject: [],
    plugins: [
      flowPlugin(/\.(js|jsx)$/, { all: true }),
      sassPlugin,
      imagePlugin,
      fontPlugin,
    ],
    loader: {
      '.js': 'jsx',
      '.jsx': 'jsx',
    },
    resolveExtensions: ['.js', '.jsx', '.json'],
    // Add node_modules paths for resolution
    nodePaths: [
      path.join(__dirname, 'node_modules'),
    ],
    // Alias for Node.js built-ins that need browser polyfills
    alias: {
      // Use native URL API for browser instead of Node's url module
      'url': require.resolve('./polyfills/url-browser.js'),
    },
    // Include dancedeets-common in the bundle (don't treat as external)
    external: [],
  });

  // Extract actual output filename from metafile
  const outputs = Object.keys(result.metafile.outputs);
  const jsOutput = outputs.find(o => o.endsWith('.js') && !o.endsWith('.js.map'));

  if (jsOutput) {
    const jsFilename = path.basename(jsOutput);
    assetManifest[`${name}.js`] = jsFilename;

    // Read the generated JS to compute content hash if needed
    if (isProd && !jsFilename.includes('[hash]')) {
      const jsContent = fs.readFileSync(path.join(__dirname, jsOutput));
      const hash = contentHash(jsContent);
      const hashedName = `${name}.${hash}.js`;
      const srcPath = path.join(__dirname, jsOutput);
      const destPath = path.join(jsDir, hashedName);

      fs.renameSync(srcPath, destPath);
      assetManifest[`${name}.js`] = hashedName;

      // Also rename source map if it exists
      const mapSrc = srcPath + '.map';
      if (fs.existsSync(mapSrc)) {
        fs.renameSync(mapSrc, destPath + '.map');
      }
    }
  }

  return result;
}

/**
 * Extract collected CSS to files
 */
function extractCSS() {
  // Create reverse mapping from entry path to entry name
  const pathToName = {};
  for (const [name, entryPath] of Object.entries(entryPoints)) {
    pathToName[entryPath] = name;
  }

  for (const [entryPath, cssArray] of cssContentsByPath.entries()) {
    const name = pathToName[entryPath];
    if (!name) continue;

    const cssContent = cssArray.join('\n');
    if (cssContent.trim()) {
      let cssFilename;
      if (isProd) {
        const hash = contentHash(cssContent);
        cssFilename = `${name}.${hash}.css`;
      } else {
        cssFilename = `${name}.css`;
      }

      fs.writeFileSync(path.join(cssDir, cssFilename), cssContent);
      assetManifest[`${name}.css`] = cssFilename;
    }
  }
}

/**
 * Write manifest.json for production builds
 */
function writeManifest() {
  if (isProd) {
    const manifestPath = path.join(distDir, 'manifest-esbuild.json');
    fs.writeFileSync(manifestPath, JSON.stringify(assetManifest, null, 2));
    console.log('Generated manifest:', manifestPath);
  }
}

async function build() {
  const start = Date.now();

  try {
    console.log(`Building ${Object.keys(entryPoints).length} entry points...`);
    console.log(`Mode: ${isProd ? 'production' : 'development'}`);

    // Clean output directories before build
    cleanOutputDirs();

    // Build all entry points
    const buildPromises = Object.entries(entryPoints).map(([name, entry]) =>
      buildEntry(name, entry)
    );

    await Promise.all(buildPromises);

    // Extract CSS files
    extractCSS();

    // Write manifest
    writeManifest();

    console.log(`Build completed in ${Date.now() - start}ms`);
    console.log(`Output: ${jsDir}`);

  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

async function watch() {
  console.log('Watch mode is not yet implemented for client builds');
  console.log('Use webpack for development with watch mode');
  // For a full implementation, we'd need to use esbuild.context() and ctx.watch()
  // But CSS extraction makes this more complex
  process.exit(1);
}

if (isWatch) {
  watch();
} else {
  build();
}
