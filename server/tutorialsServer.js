/**
 * MVP Express server for DanceDeets Tutorials
 *
 * This is a standalone Node.js server that serves the tutorials
 * without requiring the Python/GAE backend.
 *
 * Usage: node tutorialsServer.js [--port 3000]
 */

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from dist directory
app.use('/dist', express.static(path.join(__dirname, 'dist')));

// Serve Font Awesome from node_modules
app.use('/fonts', express.static(path.join(__dirname, 'node_modules/font-awesome/fonts')));
app.use('/css/font-awesome.min.css', express.static(path.join(__dirname, 'node_modules/font-awesome/css/font-awesome.min.css')));

// HTML template for tutorials
function tutorialTemplate(props, scriptName, title) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | DanceDeets Tutorials</title>
  <link rel="stylesheet" href="/css/font-awesome.min.css">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #f5f5f5;
      min-height: 100%;
    }
    a { color: #4a4a8a; }
    .navbar {
      background: #333;
      color: white;
      padding: 15px 20px;
      margin-bottom: 0;
      height: 50px;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
    }
    .navbar h1 { font-size: 20px; margin: 0; }
    .navbar a { color: white; text-decoration: none; }
    .body-contents {
      margin-top: 50px;
      padding: 10px;
    }
    #react-parent {
      min-height: calc(100vh - 50px);
    }
    /* YouTube player responsive wrapper */
    .youtube-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    .youtube-container iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    /* Responsive video layout */
    .video-player-container {
      flex: 2;
      width: 66.666%;
      max-height: 100%;
    }

    /* Tutorial page specific - fixed height container */
    .media-width-row-or-column {
      max-height: calc(100vh - 50px);
    }

    /* On mobile/narrow screens, stack vertically */
    @media (max-width: 900px) {
      .media-width-row-or-column {
        flex-direction: column !important;
      }
      .video-player-container {
        width: 100%;
        flex: none;
      }
    }
  </style>
</head>
<body>
  <nav class="navbar">
    <h1><a href="/tutorials">DanceDeets Tutorials</a></h1>
  </nav>
  <div id="react-parent" class="body-contents">
    <!-- React will render here -->
  </div>
  <script>
    // Mock global variables expected by the app
    window.prodMode = false;
    window.fbPermissions = '';
    window.fbAppId = '';
    window.baseHostname = 'localhost';
    window.showSmartBanner = false;
    window.mixpanel = { track: function() {} };
    window.sentMixpanelPing = false;

    // Detect locale from browser
    var browserLocale = navigator.language || navigator.userLanguage || 'en-US';

    window._REACT_PROPS = ${JSON.stringify(props)};
    // Override currentLocale with browser locale if not already set
    if (!window._REACT_PROPS.currentLocale) {
      window._REACT_PROPS.currentLocale = browserLocale;
    }
    window._REACT_ID = 'react-parent';
  </script>
  <script src="/dist/js/${scriptName}.js"></script>
</body>
</html>
`;
}

// Tutorials category page (list all tutorials)
app.get('/tutorials', (req, res) => {
  const props = {
    hashLocation: '',
    // currentLocale will be set by browser detection in the template
  };
  res.send(tutorialTemplate(props, 'tutorialCategoryExec', 'All Tutorials'));
});

// Individual tutorial page
app.get('/tutorials/:style/:tutorialId', (req, res) => {
  const { style, tutorialId } = req.params;
  const tutorial = `${style}/${tutorialId}`;
  const props = {
    tutorial,
    style,
    hashLocation: '',
    // currentLocale will be set by browser detection in the template
  };
  res.send(tutorialTemplate(props, 'tutorialExec', `${tutorialId} - ${style}`));
});

// Redirect root to tutorials
app.get('/', (req, res) => {
  res.redirect('/tutorials');
});

// Start server
app.listen(PORT, () => {
  console.log(`
=================================================
  DanceDeets Tutorials Server
=================================================

  Server running at: http://localhost:${PORT}

  Available pages:
    - http://localhost:${PORT}/tutorials
    - http://localhost:${PORT}/tutorials/break/vincanitv-beginner
    - http://localhost:${PORT}/tutorials/hiphop/nextschool-dictionary
    - http://localhost:${PORT}/tutorials/pop/oldschool-dictionary

=================================================
`);
});
