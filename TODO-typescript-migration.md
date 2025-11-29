# TypeScript Migration - Remaining Work

This document tracks remaining TypeScript errors after the Flow to TypeScript migration.

## Current Status

- **196 TypeScript errors remaining** (reduced from 265)
- Run `npx tsc --noEmit` to see all current errors

## How to Check Remaining Errors

```bash
# Count total errors
npx tsc --noEmit 2>&1 | grep "error TS" | wc -l

# See error summary by type
npx tsc --noEmit 2>&1 | grep "error TS" | sed 's/.*error /error /' | sort | uniq -c | sort -rn

# See all errors
npx tsc --noEmit
```

## Remaining Issues by Category

### 1. Redux connect() Type Mismatches (~31 errors)

**Problem:** `react-redux` `connect()` function has strict typing that conflicts with our `Dispatch` type which includes `ThunkAction`.

**Files affected:**
- `mobile/js/ScreenshotSlideshow.tsx`
- `mobile/js/containers/Profile.tsx`
- Various other connected components

**Solution options:**
- Use `ConnectedProps` helper from react-redux
- Add proper typing for thunk dispatch
- Consider using `useDispatch`/`useSelector` hooks instead of `connect()`

### 2. React Native Deprecated APIs (~6 errors)

**Problem:** `AsyncStorage`, `AlertIOS`, `WebView` were deprecated and moved to separate packages.

**Files affected:**
- `mobile/js/notifications/prefs.ts` - uses `AsyncStorage`
- `mobile/js/login/savedState.ts` - uses `AsyncStorage`
- `mobile/js/events/savedAddress.ts` - uses `AsyncStorage`
- `mobile/js/containers/Profile.tsx` - uses `AlertIOS`
- `mobile/js/learn/playlistViews.tsx` - uses `AlertIOS`
- `mobile/js/events/uicomponents.tsx` - uses `AlertIOS`
- `mobile/js/containers/TabNavigator.tsx` - uses `WebView`

**Solution options:**
- Install `@react-native-async-storage/async-storage` and update imports
- Replace `AlertIOS` with `Alert.alert()` (cross-platform)
- Install `react-native-webview` and update imports
- Or add type declarations if keeping deprecated APIs for now

### 3. react-native-permissions API Changes (~3 errors)

**Problem:** API changed in newer versions (`canOpenSettings` -> `openSettings`, `StatusAuthorized` removed)

**Files affected:**
- `mobile/js/api/calendar.ts`

**Solution:** Update to match current react-native-permissions API or pin types to older version

### 4. Video Player Property Issues (~11 errors)

**Problem:** `MyVideoPlayer` class missing type declarations for `animations`, `player`, `renderControl` properties

**Files affected:**
- `mobile/js/learn/playlistViews.tsx`

**Solution:** Add proper property declarations to `MyVideoPlayer` class

### 5. TrackFirebase Component Props (~5 errors)

**Problem:** Component expects `children` and `firebaseData` props but receives different props

**Files affected:**
- `mobile/js/containers/screens/Battle.tsx`

**Solution:** Update component usage to match expected props interface

### 6. IntlShape Type Mismatches (~3 errors)

**Problem:** Custom intl objects don't match full `IntlShape` interface

**Files affected:**
- Various files creating partial intl objects

**Solution:** Ensure intl objects include all required properties or use proper typing

### 7. FlatList/Card Component Props (~multiple errors)

**Problem:** Missing required props like `title` for Card, `renderHeader` vs `ListHeaderComponent` for FlatList

**Files affected:**
- `mobile/js/containers/Profile.tsx`
- `mobile/js/event_signups/battleEventHostView.tsx`
- `mobile/js/event_signups/battleHostCategoryView.tsx`

**Solution:** Update component usage to use correct prop names for current library versions

## Files with Most Errors

To find files with most errors:
```bash
npx tsc --noEmit 2>&1 | grep "error TS" | cut -d'(' -f1 | sort | uniq -c | sort -rn | head -20
```

## Priority Order for Fixes

1. **High:** Redux connect() issues - affects many components
2. **High:** Deprecated React Native APIs - will break in future RN versions
3. **Medium:** Video player types - localized to learn module
4. **Medium:** TrackFirebase props - localized to Battle screens
5. **Low:** IntlShape mismatches - runtime still works

## Notes

- The mobile package uses a linked local react-native (`file:../../react-native`)
- react-intl is pinned to v2.4.0 (uses `InjectedIntlProps`, not `WrappedComponentProps`)
- Many type declarations are in `mobile/types/modules.d.ts`
