# DanceDeets Tutorials Server

This is a standalone Node.js Express server that serves the DanceDeets tutorials application without requiring the Python/GAE backend.

## Quick Start

```bash
# 1. Install dependencies
npm install --legacy-peer-deps --ignore-scripts

# 2. Build the frontend bundles
npx webpack --config webpack.config.tutorials.js

# 3. Start the server
node tutorialsServer.js
```

The server will start on `http://localhost:3000`

## Available Pages

- **All Tutorials**: http://localhost:3000/tutorials
- **Individual Tutorial Examples**:
  - http://localhost:3000/tutorials/break/vincanitv-beginner
  - http://localhost:3000/tutorials/hiphop/nextschool-dictionary
  - http://localhost:3000/tutorials/pop/oldschool-dictionary

## Architecture

### Server (`tutorialsServer.js`)

- Express server running on port 3000 (configurable via `PORT` env var)
- Serves static assets from `/dist` directory
- Provides two main routes:
  - `/tutorials` - Lists all tutorials with filtering
  - `/tutorials/:style/:tutorialId` - Individual tutorial player page
- Includes browser locale detection for i18n

### Frontend Bundles

Built with webpack from these entry points:
- `tutorialCategoryExec.js` - Tutorial listing/filtering page
- `tutorialExec.js` - Individual tutorial player page

### Key Features

1. **Responsive Layout**
   - Desktop (>900px): Video player and playlist side-by-side
   - Mobile (≤900px): Stacked vertically

2. **Lazy Loading**
   - First 6 tutorial thumbnails load immediately
   - Remaining thumbnails lazy-load as you scroll
   - Uses window scroll detection (not nested scroll containers)

3. **Internationalization**
   - Automatically detects browser locale
   - Falls back to 'en-US' if not detected

4. **Tutorial Filtering**
   - Filter by dance style (Breaking, Hip Hop, Popping, etc.)
   - Filter by language (English, Spanish, Japanese, etc.)
   - Search by keywords (teacher name, move name, etc.)

## Development

### Building

The webpack build creates two bundles:
```bash
npx webpack --config webpack.config.tutorials.js
```

This generates:
- `dist/js/tutorialCategoryExec.js` - Tutorial list page
- `dist/js/tutorialExec.js` - Tutorial player page

### Watching for Changes

For development with auto-rebuild:
```bash
npx webpack --config webpack.config.tutorials.js --watch
```

### Running the Server

```bash
# Default port (3000)
node tutorialsServer.js

# Custom port
PORT=8080 node tutorialsServer.js
```

### Restarting After Changes

If the server is already running:
```bash
lsof -ti:3000 | xargs kill -9 2>/dev/null && node tutorialsServer.js
```

Or for a clean rebuild and restart:
```bash
npx webpack --config webpack.config.tutorials.js && \
lsof -ti:3000 | xargs kill -9 2>/dev/null && \
node tutorialsServer.js
```

## Technical Details

### Dependencies

Key packages:
- **express**: Web server
- **react**: UI framework
- **react-intl**: Internationalization
- **react-lazyload**: Image lazy loading
- **react-masonry-component**: Grid layout for tutorial cards
- **react-youtube**: YouTube player integration
- **webpack**: Module bundler
- **babel**: JavaScript transpiler (ES6/Flow to ES5)

### Babel Configuration

The webpack config uses:
- `babel-preset-latest`: Modern JavaScript support
- `babel-preset-react`: JSX transformation
- `babel-preset-stage-0`: Experimental features
- `babel-plugin-transform-flow-strip-types`: Flow type removal

All babel presets/plugins use `require.resolve()` to ensure proper resolution from server's `node_modules`.

### Common Issues & Solutions

#### 1. Module Not Found Errors

**Problem**: Webpack can't find babel plugins or dependencies

**Solution**: The webpack config uses `require.resolve()` for all babel presets/plugins:
```javascript
presets: [
  [require.resolve('babel-preset-latest'), { es2015: { modules: false } }],
  require.resolve('babel-preset-react'),
  require.resolve('babel-preset-stage-0'),
]
```

## File Structure

```
server/
├── tutorialsServer.js           # Express server
├── webpack.config.tutorials.js  # Webpack build config
├── package.json                 # Dependencies
├── assets/js/
│   ├── tutorialExec.js         # Tutorial player entry point
│   ├── tutorial.js             # Tutorial player component
│   ├── tutorialCategoryExec.js # Tutorial list entry point
│   ├── tutorialCategory.js     # Tutorial list component
│   ├── renderReact.js          # React rendering helper
│   ├── ui.js                   # Shared UI components
│   └── ...
├── dist/js/                    # Built bundles (generated)
└── node_modules/               # Dependencies (generated)
```

## Tutorial Data

Tutorial data comes from the shared `dancedeets-common` package:
- `dancedeets-common/js/tutorials/playlistConfig.js` - Tutorial definitions
- `dancedeets-common/js/tutorials/models.js` - Data models (Playlist, Video, Section)

## CSS & Styling

The server uses inline styles in the HTML template with:
- Fixed navbar (50px height)
- Responsive YouTube player with 16:9 aspect ratio
- Mobile-first responsive breakpoints
- Font Awesome for icons

## Port Management

If you get "port already in use" errors:
```bash
# Find process using port 3000
lsof -ti:3000

# Kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

## Mock Globals

The server provides mock globals for client-side code:
```javascript
window.prodMode = false;
window.fbPermissions = '';
window.fbAppId = '';
window.baseHostname = 'localhost';
window.showSmartBanner = false;
window.mixpanel = { track: function() {} };
```

These prevent errors from code expecting the full production environment.

## Future Improvements

Potential enhancements:
1. Server-side rendering for faster initial load
2. Production build optimization (minification, code splitting)
3. Hot module replacement for faster development
4. API endpoint for tutorial data (currently embedded)
5. CDN integration for static assets
6. Service worker for offline support
