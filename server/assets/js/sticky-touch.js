/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

// This is because of sticky touch CSS on mobile devices:
// https://github.com/twbs/bootstrap/issues/12832
// With bootstrap v4, we can replace this with:
// http://v4-alpha.getbootstrap.com/getting-started/browsers-devices/#sticky-hoverfocus-on-mobile
// For other solutions, see:
// http://stackoverflow.com/questions/17233804/how-to-prevent-sticky-hover-effects-for-buttons-on-touch-devices
// http://stackoverflow.com/questions/23885255/how-to-remove-ignore-hover-css-style-on-touch-devices?lq=1
function fixStickyTouch() {
  const touch =
    'ontouchstart' in window ||
    window.navigator.MaxTouchPoints > 0 ||
    window.navigator.msMaxTouchPoints > 0;

  if (touch) {
    // remove all :hover stylesheets
    try {
      // prevent crash on browsers not supporting DOM styleSheets properly
      const keepSelectors = [];
      const keepNonHoverSelectors = s => {
        if (!s.match(':hover')) {
          keepSelectors.push(s);
        }
      };
      for (const si of window.document.styleSheets) {
        const styleSheet = window.document.styleSheets[si];
        if (styleSheet.rules) {
          for (let ri = styleSheet.rules.length - 1; ri >= 0; ri -= 1) {
            const st = styleSheet.rules[ri].selectorText;
            if (st) {
              if (st.match(':hover')) {
                if (st.indexOf(',') === -1) {
                  styleSheet.deleteRule(ri);
                } else {
                  const selectors = st.split(',');
                  keepSelectors.length = 0;
                  selectors.forEach(keepNonHoverSelectors);
                  const newSelectorText = keepSelectors.join(',');
                  styleSheet.rules[ri].selectorText = newSelectorText;
                }
              }
            }
          }
        }
      }
    } catch (ex) {
      // Do nothing
    }
  }
}

module.exports = fixStickyTouch;
