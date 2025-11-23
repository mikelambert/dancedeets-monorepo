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
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #f5f5f5;
    }
    a { color: #4a4a8a; }
    .navbar {
      background: #333;
      color: white;
      padding: 15px 20px;
      margin-bottom: 0;
    }
    .navbar h1 { font-size: 20px; margin: 0; }
    .navbar a { color: white; text-decoration: none; }
    .body-contents { margin-top: 0; }
  </style>
</head>
<body>
  <nav class="navbar">
    <h1><a href="/tutorials">DanceDeets Tutorials</a></h1>
  </nav>
  <div id="react-parent" class="body-contents">
    <!-- React will render here -->
    <div style="padding: 20px; text-align: center;">Loading tutorials...</div>
  </div>
  <script>
    // Mock global variables expected by the app
    window.prodMode = false;
    window.fbPermissions = '';
    window.fbAppId = '';
    window.baseHostname = 'localhost';
    window.showSmartBanner = false;
    window.mixpanel = { track: function() {} };
    window._REACT_PROPS = ${JSON.stringify(props)};
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
