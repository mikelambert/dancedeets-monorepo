package com.dancedeets.android;

import android.app.Application;
import android.os.Build;
import android.support.multidex.MultiDexApplication;
import android.util.Log;

import com.BV.LinearGradient.LinearGradientPackage;
import com.airbnb.android.react.maps.MapsPackage;
import com.burnweb.rnsendintent.RNSendIntentPackage;
import com.chirag.RNMail.RNMail;
import com.crashlytics.android.Crashlytics;
import com.devfd.RNGeocoder.RNGeocoderPackage;
import com.dieam.reactnativepushnotification.ReactNativePushNotificationPackage;
import com.facebook.CallbackManager;
import com.facebook.FacebookSdk;
import com.facebook.appevents.AppEventsLogger;
import com.facebook.react.ReactApplication;
import com.apsl.versionnumber.RNVersionNumberPackage;
import io.invertase.firebase.RNFirebasePackage;
import com.brentvatne.react.ReactVideoPackage;
import io.sentry.RNSentryPackage;
import com.oblador.vectoricons.VectorIconsPackage;
import com.learnium.RNDeviceInfo.RNDeviceInfo;
import com.facebook.react.ReactNativeHost;
import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainReactPackage;
import com.facebook.reactnative.androidsdk.FBSDKPackage;
import com.facebook.soloader.SoLoader;
import com.google.firebase.crash.FirebaseCrash;
import com.higo.zhangyp.segmented.AndroidSegmentedPackage;
import com.inprogress.reactnativeyoutube.ReactNativeYouTube;
import com.kevinejohn.RNMixpanel.RNMixpanel;
import com.microsoft.codepush.react.CodePush;
import com.microsoft.codepush.react.ReactInstanceHolder;
import com.reactnative.photoview.PhotoViewPackage;
import com.smixx.fabric.FabricPackage;

import org.jall.reactnative.firebase.FirebasePackage;
import org.jall.reactnative.googleapiavailability.GoogleApiAvailabilityPackage;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Arrays;
import java.util.List;

import cl.json.RNSharePackage;
import io.fabric.sdk.android.Fabric;
import io.fixd.rctlocale.RCTLocalePackage;

// Use a separate MyReactNativeHost class as suggested by the react-native-code-push docs:
class MyReactNativeHost extends ReactNativeHost implements ReactInstanceHolder {

  protected MyReactNativeHost(Application application) {
    super(application);
  }

  static CallbackManager mCallbackManager = CallbackManager.Factory.create();

  @Override
  public boolean getUseDeveloperSupport() {
    return BuildConfig.DEBUG;
  }

  @Override
  protected List<ReactPackage> getPackages() {
    return Arrays.<ReactPackage>asList(
      new MainReactPackage(),
            new RNVersionNumberPackage(),
            new RNFirebasePackage(),
            new RNFirebaseAnalyticsPackage(),
            new RNFirebaseRemoteConfigPackage(),
            new RNFirebaseDatabasePackage(),
            new ReactVideoPackage(),
      new RNSentryPackage((ReactApplication)getApplication()),
      new VectorIconsPackage(),
      new RNDeviceInfo(),
      new ReactNativeYouTube(),
      new GoogleApiAvailabilityPackage(),
      new ReactNativePushNotificationPackage(),
      new PhotoViewPackage(),
      new FirebasePackage(),
      new RCTNativeEnvPackage(BuildConfig.class),
      new RCTLocalePackage(),
      new CodePush(BuildConfig.CODEPUSH_KEY, getApplication(), BuildConfig.DEBUG),
      new RNSharePackage(),
      new RNMail(),
      new RNMixpanel(),
      new RNGeocoderPackage(),
      new MapsPackage(),
      new FabricPackage(),
      new LinearGradientPackage(),
      new AndroidSegmentedPackage(),
      new RNSendIntentPackage(),
      new FBSDKPackage(mCallbackManager)
    );
  }

  @Override
  protected String getJSBundleFile() {
    return CodePush.getBundleUrl();
  }
}

public class MainApplication extends MultiDexApplication implements ReactApplication {
  private final MyReactNativeHost mReactNativeHost = new MyReactNativeHost(this);

  protected static CallbackManager getCallbackManager() {
    return MyReactNativeHost.mCallbackManager;
  }

  @Override
  public void onCreate() {
    super.onCreate();
    if (BuildConfig.DEBUG) {
      FirebaseCrash.setCrashCollectionEnabled(false);
    }
    // If we want to have Crashlytics report the version of our JS (and not our app),
    // because we are using CodePush or AppHub, then we need to pass in a stubbed Context.
    // It will wrap-and-delegate-to-"this", except for:
    //   PackageManager packageManager = context.getPackageManager();
    //   PackageInfo packageInfo = packageManager.getPackageInfo(this.packageName, 0);
    //   this.versionCode = Integer.toString(packageInfo.versionCode);
    //   this.versionName = (packageInfo.versionName == null ? "0.0" : packageInfo.versionName);
    Fabric.with(this, new Crashlytics());

    // Initialize the SDK before executing any other operations,
    FacebookSdk.sdkInitialize(getApplicationContext());
    AppEventsLogger.activateApp(this);
    CodePush.setReactInstanceHolder(mReactNativeHost);
    SoLoader.init(this, /* native exopackage */ false);
  }

  @Override
  public ReactNativeHost getReactNativeHost() {
    return mReactNativeHost;
  }
}
