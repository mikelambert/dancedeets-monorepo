# DanceDeets - The React-Native Version

## Install

This project uses React Native 0.72 with React 18.

```
cd dancedeets-monorepo/mobile/
npm install
```

## Release

- For iOS: Build a release within iTunes and do it the normal way
- For Android: Run `scripts/release-android.sh`, and upload the APK to the Google Play Store

## Code Layout

- [`js/`](js): All our JS code, and 99% of the real codebase
- [`ios/`](ios) and [`android/`](android): Any platform-specific code, where our RN-integrations go. Basically just wrapper and skeleton framework code.
- [`scripts/`](scripts): Some old scripts that operate on this project. Some might need to be moved up a directory (ie translation scripts).

## Migration Notes

### React Native 0.72 Upgrade (from 0.45)

The following deprecated APIs have been updated:
- **AsyncStorage**: Moved from `react-native` to `@react-native-async-storage/async-storage`
- **AlertIOS**: Replaced with cross-platform `Alert`
- **WebView**: Replaced `react-native-wkwebview-reborn` with `react-native-webview`

### Remaining Migration Work

The following components still use the deprecated `ListView` API and should be migrated to `FlatList` or `SectionList`:

1. **`js/ui/ProgressiveLayout.tsx`** - Uses `ListView.DataSource`
2. **`js/learn/playlistViews.tsx`** - Uses `ListView`
3. **`js/learn/BlogList.tsx`** - Uses `ListView.DataSource` and `<ListView>` component

The `ListView` to `FlatList` migration involves:
- Replace `ListView.DataSource` with direct array data
- Replace `<ListView>` with `<FlatList>` or `<SectionList>`
- Update `renderRow` to `renderItem` (receives `{item, index}` instead of just `item`)
- Remove `dataSource.cloneWithRows()` calls

### Legacy Fork

Previously used a patched React Native 0.45 from mikelambert/react-native with two cherrypicks. These patches are no longer needed in React Native 0.72+.
