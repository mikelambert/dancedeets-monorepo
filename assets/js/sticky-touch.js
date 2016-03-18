// This is because of sticky touch CSS on mobile devices:
// https://github.com/twbs/bootstrap/issues/12832
// With bootstrap v4, we can replace this with:
// http://v4-alpha.getbootstrap.com/getting-started/browsers-devices/#sticky-hoverfocus-on-mobile
// For other solutions, see:
// http://stackoverflow.com/questions/17233804/how-to-prevent-sticky-hover-effects-for-buttons-on-touch-devices
// http://stackoverflow.com/questions/23885255/how-to-remove-ignore-hover-css-style-on-touch-devices?lq=1
function fixStickyTouch(window) {
  var touch = 'ontouchstart' in window ||
          window.navigator.MaxTouchPoints > 0 ||
          window.navigator.msMaxTouchPoints > 0;

  if (touch) { // remove all :hover stylesheets
    try { // prevent crash on browsers not supporting DOM styleSheets properly
      var keepSelectors = [];
      var keepNonHoverSelectors = function(s) {
        if (!s.match(':hover')) {
          keepSelectors.push(s);
        }
      };
      for (var si in window.document.styleSheets) {
        if (window.document.styleSheets.hasOwnProperty(si)) {
          var styleSheet = window.document.styleSheets[si];
          if (!styleSheet.rules) {
            continue;
          }

          for (var ri = styleSheet.rules.length - 1; ri >= 0; ri--) {
            var st = styleSheet.rules[ri].selectorText;
            if (st) {
              if (st.match(':hover')) {
                if (st.indexOf(',') === -1) {
                  styleSheet.deleteRule(ri);
                } else {
                  var selectors = st.split(',');
                  keepSelectors.length = 0;
                  selectors.forEach(keepNonHoverSelectors);
                  var newSelectorText = keepSelectors.join(',');
                  styleSheet.rules[ri].selectorText = newSelectorText;
                }
              }
            }
          }
        }
      }
    } catch (ex) {}
  }
}

module.exports = fixStickyTouch;
