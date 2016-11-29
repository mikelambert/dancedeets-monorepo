# DanceDeets - The React-Native Version

## Install

This uses a slightly patched version of react-native 0.33 (two cherrypicks from post-0.33):

```
cd react-native
./gradlew :ReactAndroid:installArchives
cd ../dancedeets-react5/
npm install react-native
```

We could alternately (un)comment the `React-Native-Compile:` sections and build react-native as part of our build. But it's slower in a variety of ways, so I'd prefer to avoid that as long as we don't need to actively develop React Native.
