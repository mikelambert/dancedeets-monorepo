/**
 * esbuild configuration for common/ package
 * Generates both CJS and ESM output formats for dual-package support
 *
 * Usage:
 *   node esbuild.config.js           # Build both formats
 *   node esbuild.config.js --watch   # Watch mode (not yet implemented)
 *
 * Output:
 *   - ESM: dist/esm/
 *   - CJS: dist/cjs/
 *   - Types: dist/types/ (via tsc)
 */

const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const isWatch = process.argv.includes('--watch');

// Directories
const srcDir = path.join(__dirname, 'js');
const distDir = path.join(__dirname, 'dist');
const esmDir = path.join(distDir, 'esm');
const cjsDir = path.join(distDir, 'cjs');

/**
 * Find all TypeScript entry points (excluding test files)
 */
function findEntryPoints() {
  const entries = [];

  function walkDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        // Skip test directories
        if (file === '__tests__') continue;
        walkDir(filePath);
      } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
        // Skip test files
        if (file.includes('.test.')) continue;
        entries.push(filePath);
      }
    }
  }

  walkDir(srcDir);
  return entries;
}

/**
 * Copy JSON files to output directories maintaining structure
 */
function copyJsonFiles() {
  function walkDir(dir, relativePath = '') {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        // Skip test directories
        if (file === '__tests__') continue;
        walkDir(filePath, path.join(relativePath, file));
      } else if (file.endsWith('.json')) {
        // Copy to both ESM and CJS directories
        const esmDest = path.join(esmDir, relativePath, file);
        const cjsDest = path.join(cjsDir, relativePath, file);

        fs.mkdirSync(path.dirname(esmDest), { recursive: true });
        fs.mkdirSync(path.dirname(cjsDest), { recursive: true });

        fs.copyFileSync(filePath, esmDest);
        fs.copyFileSync(filePath, cjsDest);
      }
    }
  }

  walkDir(srcDir);
}

/**
 * Clean output directories
 */
function cleanDist() {
  if (fs.existsSync(distDir)) {
    fs.rmSync(distDir, { recursive: true });
  }
  fs.mkdirSync(esmDir, { recursive: true });
  fs.mkdirSync(cjsDir, { recursive: true });
}

/**
 * Build TypeScript declarations using tsc
 */
function buildTypes() {
  console.log('Generating TypeScript declarations...');
  try {
    execSync('npx tsc --project tsconfig.json', {
      cwd: __dirname,
      stdio: 'inherit',
    });
    console.log('TypeScript declarations generated');
  } catch (error) {
    console.error('Failed to generate TypeScript declarations');
    // Don't fail the build - types are optional
  }
}

/**
 * Common esbuild options
 * Note: bundle is false to preserve module structure (each file is transpiled independently)
 * Dependencies are resolved at runtime by the consuming application
 */
function getCommonOptions(entryPoints) {
  return {
    entryPoints,
    bundle: false, // Don't bundle - preserve module structure
    platform: 'neutral', // Works for both Node and browser
    target: ['es2017'],
    sourcemap: true,
    resolveExtensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
    loader: {
      '.ts': 'ts',
      '.tsx': 'tsx',
    },
  };
}

/**
 * Build ESM output
 */
async function buildESM(entryPoints) {
  console.log('Building ESM output...');

  await esbuild.build({
    ...getCommonOptions(entryPoints),
    outdir: esmDir,
    format: 'esm',
    outExtension: { '.js': '.js' },
  });

  // Create package.json for ESM directory
  fs.writeFileSync(
    path.join(esmDir, 'package.json'),
    JSON.stringify({ type: 'module' }, null, 2)
  );

  console.log('ESM build complete');
}

/**
 * Build CJS output
 */
async function buildCJS(entryPoints) {
  console.log('Building CJS output...');

  await esbuild.build({
    ...getCommonOptions(entryPoints),
    outdir: cjsDir,
    format: 'cjs',
    outExtension: { '.js': '.cjs' },
  });

  // Create package.json for CJS directory
  fs.writeFileSync(
    path.join(cjsDir, 'package.json'),
    JSON.stringify({ type: 'commonjs' }, null, 2)
  );

  console.log('CJS build complete');
}

/**
 * Main build function
 */
async function build() {
  const start = Date.now();

  try {
    console.log('Building dancedeets-common package...\n');

    // Clean output directories
    cleanDist();

    // Find all entry points
    const entryPoints = findEntryPoints();
    console.log(`Found ${entryPoints.length} entry points\n`);

    // Build both formats in parallel
    await Promise.all([
      buildESM(entryPoints),
      buildCJS(entryPoints),
    ]);

    // Copy JSON files
    console.log('\nCopying JSON files...');
    copyJsonFiles();

    // Generate TypeScript declarations
    console.log('');
    buildTypes();

    console.log(`\nBuild completed in ${Date.now() - start}ms`);
    console.log(`Output: ${distDir}`);

  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

async function watch() {
  console.log('Watch mode is not yet implemented');
  process.exit(1);
}

if (isWatch) {
  watch();
} else {
  build();
}
