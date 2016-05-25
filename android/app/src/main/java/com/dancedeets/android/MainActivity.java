package com.dancedeets.android;

import android.content.Intent;
import android.os.Bundle;

import com.AirMaps.AirPackage;
import com.BV.LinearGradient.LinearGradientPackage;
import com.burnweb.rnsendintent.RNSendIntentPackage;
import com.crashlytics.android.Crashlytics;
import com.devfd.RNGeocoder.RNGeocoderPackage;
import com.facebook.CallbackManager;
import com.facebook.FacebookSdk;
import com.facebook.appevents.AppEventsLogger;
import com.facebook.react.ReactActivity;
import com.kevinejohn.RNMixpanel.RNMixpanel;
import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainReactPackage;
import com.facebook.reactnative.androidsdk.FBSDKPackage;
import com.higo.zhangyp.segmented.AndroidSegmentedPackage;
import com.kevinejohn.RNMixpanel.RNMixpanel;
import com.smixx.fabric.FabricPackage;

import java.util.Arrays;
import java.util.List;

import io.fabric.sdk.android.Fabric;

public class MainActivity extends ReactActivity {
    CallbackManager mCallbackManager;

    /**
     * Returns the name of the main component registered from JavaScript.
     * This is used to schedule rendering of the component.
     */
    @Override
    protected String getMainComponentName() {
        return "DanceDeets";
    }

    /**
     * Returns whether dev mode should be enabled.
     * This enables e.g. the dev menu.
     */
    @Override
    protected boolean getUseDeveloperSupport() {
        return BuildConfig.DEBUG;
    }

    /**
     * A list of packages used by the app. If the app uses additional views
     * or modules besides the default ones, add more packages here.
     */
    @Override
    protected List<ReactPackage> getPackages() {
        mCallbackManager = CallbackManager.Factory.create();
        return Arrays.<ReactPackage>asList(
            new MainReactPackage(),
            new RNMixpanel(),
            new RNGeocoderPackage(),
            new AirPackage(),
            new FabricPackage(null),
            new LinearGradientPackage(),
            new AndroidSegmentedPackage(),
            new RNMixpanel(),
            new RNSendIntentPackage(),
            new FBSDKPackage(mCallbackManager)
        );
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        FacebookSdk.sdkInitialize(getApplicationContext());
        // If we want to have Crashlytics report the version of our JS (and not our app),
        // because we are using CodePush or AppHub, then we need to pass in a stubbed Context.
        // It will wrap-and-delegate-to-"this", except for:
        //   PackageManager packageManager = context.getPackageManager();
        //   PackageInfo packageInfo = packageManager.getPackageInfo(this.packageName, 0);
        //   this.versionCode = Integer.toString(packageInfo.versionCode);
        //   this.versionName = (packageInfo.versionName == null ? "0.0" : packageInfo.versionName);
        Fabric.with(this, new Crashlytics());
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        mCallbackManager.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    protected void onResume() {
        super.onResume();
        AppEventsLogger.activateApp(getApplication());
    }

    @Override
    protected void onStop() {
        super.onStop();
        AppEventsLogger.onContextStop();
    }
}
