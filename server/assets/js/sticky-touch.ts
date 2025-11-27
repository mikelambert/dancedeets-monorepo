/**
 * Copyright 2016 DanceDeets.
 */

// This is because of sticky touch CSS on mobile devices:
// https://github.com/twbs/bootstrap/issues/12832
// With bootstrap v4, we can replace this with:
// http://v4-alpha.getbootstrap.com/getting-started/browsers-devices/#sticky-hoverfocus-on-mobile
// For other solutions, see:
// http://stackoverflow.com/questions/17233804/how-to-prevent-sticky-hover-effects-for-buttons-on-touch-devices
// http://stackoverflow.com/questions/23885255/how-to-remove-ignore-hover-css-style-on-touch-devices?lq=1

interface NavigatorWithTouch extends Navigator {
  MaxTouchPoints?: number;
  msMaxTouchPoints?: number;
}

interface CSSStyleRuleWithSelector extends CSSStyleRule {
  selectorText: string;
}

function fixStickyTouch(): void {
  const nav = window.navigator as NavigatorWithTouch;
  const touch =
    'ontouchstart' in window ||
    (nav.MaxTouchPoints ?? 0) > 0 ||
    (nav.msMaxTouchPoints ?? 0) > 0;

  if (touch) {
    // remove all :hover stylesheets
    try {
      // prevent crash on browsers not supporting DOM styleSheets properly
      const keepSelectors: string[] = [];
      const keepNonHoverSelectors = (s: string): void => {
        if (!s.match(':hover')) {
          keepSelectors.push(s);
        }
      };
      for (let si = 0; si < window.document.styleSheets.length; si++) {
        const styleSheet = window.document.styleSheets[si] as CSSStyleSheet;
        if (styleSheet.cssRules) {
          for (let ri = styleSheet.cssRules.length - 1; ri >= 0; ri -= 1) {
            const rule = styleSheet.cssRules[ri] as CSSStyleRuleWithSelector;
            const st = rule.selectorText;
            if (st) {
              if (st.match(':hover')) {
                if (st.indexOf(',') === -1) {
                  styleSheet.deleteRule(ri);
                } else {
                  const selectors = st.split(',');
                  keepSelectors.length = 0;
                  selectors.forEach(keepNonHoverSelectors);
                  const newSelectorText = keepSelectors.join(',');
                  rule.selectorText = newSelectorText;
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

export default fixStickyTouch;
