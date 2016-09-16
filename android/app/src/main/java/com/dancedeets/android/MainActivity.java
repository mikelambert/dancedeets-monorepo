package com.dancedeets.android;

import android.content.Intent;
import android.os.Bundle;

import com.crashlytics.android.Crashlytics;
import com.facebook.CallbackManager;
import com.facebook.FacebookSdk;
import com.facebook.appevents.AppEventsLogger;
import com.facebook.react.ReactActivity;

import io.fabric.sdk.android.Fabric;

public class MainActivity extends ReactActivity {
    /**
     * Returns the name of the main component registered from JavaScript.
     * This is used to schedule rendering of the component.
     */
    @Override
    protected String getMainComponentName() {
        return "DanceDeets";
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
        MainApplication.getCallbackManager().onActivityResult(requestCode, resultCode, data);
    }

    @Override
    protected void onStop() {
        super.onStop();
        AppEventsLogger.onContextStop();
    }
}
