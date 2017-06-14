# DanceDeets - The React-Native Version

## Install

This uses a slightly patched version of react-native 0.45 (two cherrypicks from post-0.45), found on mikelambert/react-native:

```
cd react-native
./gradlew :ReactAndroid:installArchives
cd ../dancedeets-monorepo/mobile/
npm install
```

We could alternately (un)comment the `React-Native-Compile:` sections and build react-native as part of our build. But it's slower in a variety of ways, so I'd prefer to avoid that as long as we don't need to actively develop React Native.

## Release

- For iOS: Build a release within iTunes and do it the normal way
- For Android: Run `scripts/release-android.sh`, and upload the APK to the Google Play Store

## Code Layout

- `js/`: All our JS code, and 99% of the real codebase
- `ios/` and `android/`: Any platform-specific code, where our RN-integrations go. Basically just wrapper and skeleton framework code.
- `scripts/`: Some old scripts that operate on this project. Some might need to be moved up a directory (ie translation scripts).
