// I think this is necessary because 'respond.js' triggers "import relative to local path" instead of the package.
// And 'respond' ends up being the wrong package. So we have to import it by relative pathname instead.
require('../../node_modules/respond.js/src/respond.js');
require('html5shiv');
require('jquery.placeholder');
