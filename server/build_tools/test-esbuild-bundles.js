#!/usr/bin/env node
/**
 * Offline test script for esbuild client bundles
 *
 * Usage:
 *   node build_tools/test-esbuild-bundles.js
 *
 * This script verifies:
 *   1. All expected bundles are generated
 *   2. JS files are syntactically valid (can be parsed by Node)
 *   3. CSS files are non-empty
 *   4. Manifest contains all expected entries
 *   5. Key dependencies are bundled (React, jQuery, etc.)
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const DIST_DIR = path.join(__dirname, '..', 'dist');
const JS_DIR = path.join(DIST_DIR, 'js-esbuild');
const CSS_DIR = path.join(DIST_DIR, 'css-esbuild');
const MANIFEST_PATH = path.join(DIST_DIR, 'manifest-esbuild.json');

// Expected entry points from esbuild.client.js
const EXPECTED_ENTRIES = [
  'addEvent',
  'bracketsExec',
  'calendarExec',
  'homepageReact',
  'homepage',
  'normalPage',
  'classResultsExec',
  'eventExec',
  'eventSearchResultsExec',
  'topicExec',
  'tutorialExec',
  'tutorialCategoryExec',
];

// Key strings that should be present in bundles (indicates dependencies are bundled)
const EXPECTED_BUNDLE_CONTENTS = {
  // React should be bundled
  'homepageReact': ['createElement', 'Component', 'render'],
  // jQuery should be bundled (most entries use it)
  'homepage': ['jQuery', 'backstretch'],
  'normalPage': ['jQuery'],
};

let testsPassed = 0;
let testsFailed = 0;

function log(message, type = 'info') {
  const prefix = {
    pass: '\x1b[32m✓\x1b[0m',
    fail: '\x1b[31m✗\x1b[0m',
    info: '\x1b[34mℹ\x1b[0m',
    warn: '\x1b[33m⚠\x1b[0m',
  };
  console.log(`${prefix[type] || ''} ${message}`);
}

function test(name, fn) {
  try {
    fn();
    testsPassed++;
    log(`${name}`, 'pass');
    return true;
  } catch (error) {
    testsFailed++;
    log(`${name}: ${error.message}`, 'fail');
    return false;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

// Test 1: Verify manifest exists and is valid JSON
function testManifestExists() {
  test('Manifest file exists', () => {
    assert(fs.existsSync(MANIFEST_PATH), `Manifest not found at ${MANIFEST_PATH}`);
  });

  test('Manifest is valid JSON', () => {
    const content = fs.readFileSync(MANIFEST_PATH, 'utf8');
    JSON.parse(content);
  });
}

// Test 2: Verify all expected entries are in manifest
function testManifestCompleteness() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  for (const entry of EXPECTED_ENTRIES) {
    test(`Manifest contains ${entry}.js`, () => {
      assert(`${entry}.js` in manifest, `Missing ${entry}.js in manifest`);
    });

    test(`Manifest contains ${entry}.css`, () => {
      assert(`${entry}.css` in manifest, `Missing ${entry}.css in manifest`);
    });
  }
}

// Test 3: Verify JS bundles exist and are syntactically valid
function testJsBundles() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  for (const entry of EXPECTED_ENTRIES) {
    const jsKey = `${entry}.js`;
    const jsFilename = manifest[jsKey];

    test(`JS bundle ${entry} exists`, () => {
      const jsPath = path.join(JS_DIR, jsFilename);
      assert(fs.existsSync(jsPath), `JS file not found: ${jsPath}`);
    });

    test(`JS bundle ${entry} is non-empty`, () => {
      const jsPath = path.join(JS_DIR, jsFilename);
      const stats = fs.statSync(jsPath);
      assert(stats.size > 1000, `JS file too small (${stats.size} bytes)`);
    });

    test(`JS bundle ${entry} is syntactically valid`, () => {
      const jsPath = path.join(JS_DIR, jsFilename);
      const content = fs.readFileSync(jsPath, 'utf8');
      // Try to parse as JavaScript using vm module
      try {
        new vm.Script(content, { filename: jsFilename });
      } catch (syntaxError) {
        throw new Error(`Syntax error: ${syntaxError.message}`);
      }
    });
  }
}

// Test 4: Verify CSS bundles exist and are non-empty
function testCssBundles() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  for (const entry of EXPECTED_ENTRIES) {
    const cssKey = `${entry}.css`;
    const cssFilename = manifest[cssKey];

    test(`CSS bundle ${entry} exists`, () => {
      const cssPath = path.join(CSS_DIR, cssFilename);
      assert(fs.existsSync(cssPath), `CSS file not found: ${cssPath}`);
    });

    test(`CSS bundle ${entry} is non-empty`, () => {
      const cssPath = path.join(CSS_DIR, cssFilename);
      const stats = fs.statSync(cssPath);
      assert(stats.size > 1000, `CSS file too small (${stats.size} bytes)`);
    });

    test(`CSS bundle ${entry} contains valid CSS`, () => {
      const cssPath = path.join(CSS_DIR, cssFilename);
      const content = fs.readFileSync(cssPath, 'utf8');
      // Basic CSS validation - should contain common CSS patterns
      assert(content.includes('{'), 'CSS missing opening brace');
      assert(content.includes('}'), 'CSS missing closing brace');
      assert(content.includes(':'), 'CSS missing property separator');
    });
  }
}

// Test 5: Verify key dependencies are bundled
function testBundleContents() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  for (const [entry, expectedStrings] of Object.entries(EXPECTED_BUNDLE_CONTENTS)) {
    const jsKey = `${entry}.js`;
    const jsFilename = manifest[jsKey];
    const jsPath = path.join(JS_DIR, jsFilename);

    if (!fs.existsSync(jsPath)) {
      log(`Skipping content check for ${entry} (file not found)`, 'warn');
      continue;
    }

    const content = fs.readFileSync(jsPath, 'utf8');

    for (const expectedString of expectedStrings) {
      test(`Bundle ${entry} contains "${expectedString}"`, () => {
        assert(
          content.includes(expectedString),
          `Expected string "${expectedString}" not found in bundle`
        );
      });
    }
  }
}

// Test 6: Verify source maps exist for production builds
function testSourceMaps() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  // Check a few bundles for source maps
  const samplesToCheck = ['normalPage', 'homepageReact', 'eventExec'];

  for (const entry of samplesToCheck) {
    const jsKey = `${entry}.js`;
    const jsFilename = manifest[jsKey];
    const mapPath = path.join(JS_DIR, jsFilename + '.map');

    test(`Source map exists for ${entry}`, () => {
      assert(fs.existsSync(mapPath), `Source map not found: ${mapPath}`);
    });

    test(`Source map for ${entry} is valid JSON`, () => {
      const content = fs.readFileSync(mapPath, 'utf8');
      const parsed = JSON.parse(content);
      assert(parsed.version === 3, 'Source map version should be 3');
      assert(Array.isArray(parsed.sources), 'Source map should have sources array');
    });
  }
}

// Test 7: Verify bundle sizes are reasonable
function testBundleSizes() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  // Define expected size ranges (min, max in bytes)
  const SIZE_EXPECTATIONS = {
    // Smaller bundles (no React)
    'normalPage.js': { min: 50000, max: 500000 },
    'homepage.js': { min: 50000, max: 500000 },
    'addEvent.js': { min: 50000, max: 500000 },
    // Larger bundles (with React and more features)
    'homepageReact.js': { min: 100000, max: 2000000 },
    'eventExec.js': { min: 100000, max: 3000000 },
    'eventSearchResultsExec.js': { min: 100000, max: 3000000 },
  };

  for (const [key, { min, max }] of Object.entries(SIZE_EXPECTATIONS)) {
    const filename = manifest[key];
    if (!filename) continue;

    const filePath = path.join(JS_DIR, filename);
    if (!fs.existsSync(filePath)) continue;

    const stats = fs.statSync(filePath);
    const sizeKB = Math.round(stats.size / 1024);

    test(`Bundle ${key} size is reasonable (${sizeKB}KB)`, () => {
      assert(
        stats.size >= min && stats.size <= max,
        `Size ${stats.size} outside expected range [${min}, ${max}]`
      );
    });
  }
}

// Test 8: Verify no obvious errors in bundle (common mistakes)
function testBundleQuality() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));

  // Check a sample of bundles for common issues
  const samplesToCheck = ['normalPage', 'homepageReact'];

  for (const entry of samplesToCheck) {
    const jsKey = `${entry}.js`;
    const jsFilename = manifest[jsKey];
    const jsPath = path.join(JS_DIR, jsFilename);

    if (!fs.existsSync(jsPath)) continue;

    const content = fs.readFileSync(jsPath, 'utf8');

    test(`Bundle ${entry} doesn't contain unresolved requires`, () => {
      // Check for common error patterns that indicate failed bundling
      assert(
        !content.includes('Cannot find module'),
        'Bundle contains "Cannot find module" error'
      );
    });

    test(`Bundle ${entry} is wrapped in IIFE`, () => {
      // esbuild IIFE format starts with (()=>{ or (() => { or (function() {
      assert(
        content.startsWith('(()=>{') || content.startsWith('(() => {') || content.startsWith('(function()'),
        'Bundle should be wrapped in IIFE'
      );
    });
  }
}

// Main execution
function main() {
  console.log('\n=== esbuild Client Bundle Tests ===\n');

  // Check if dist directories exist
  if (!fs.existsSync(JS_DIR)) {
    log(`JS directory not found: ${JS_DIR}`, 'fail');
    log('Run "NODE_ENV=production node esbuild.client.js" first', 'info');
    process.exit(1);
  }

  if (!fs.existsSync(CSS_DIR)) {
    log(`CSS directory not found: ${CSS_DIR}`, 'fail');
    log('Run "NODE_ENV=production node esbuild.client.js" first', 'info');
    process.exit(1);
  }

  // Run all test suites
  console.log('--- Manifest Tests ---');
  testManifestExists();
  testManifestCompleteness();

  console.log('\n--- JS Bundle Tests ---');
  testJsBundles();

  console.log('\n--- CSS Bundle Tests ---');
  testCssBundles();

  console.log('\n--- Bundle Contents Tests ---');
  testBundleContents();

  console.log('\n--- Source Map Tests ---');
  testSourceMaps();

  console.log('\n--- Bundle Size Tests ---');
  testBundleSizes();

  console.log('\n--- Bundle Quality Tests ---');
  testBundleQuality();

  // Summary
  console.log('\n=== Test Summary ===');
  console.log(`Passed: ${testsPassed}`);
  console.log(`Failed: ${testsFailed}`);

  if (testsFailed > 0) {
    console.log('\n\x1b[31mSome tests failed!\x1b[0m');
    process.exit(1);
  } else {
    console.log('\n\x1b[32mAll tests passed!\x1b[0m');
    process.exit(0);
  }
}

main();
