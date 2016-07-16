
import android.app.Application;
import android.util.Log;

import com.facebook.react.ReactApplication;
import com.facebook.react.ReactInstanceManager;
import com.facebook.react.ReactNativeHost;
import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainReactPackage;

import java.util.Arrays;
import java.util.List;

public class MainApplication extends Application implements ReactApplication {

  private final ReactNativeHost mReactNativeHost = new ReactNativeHost(this) {
    @Override
    protected boolean getUseDeveloperSupport() {
      return BuildConfig.DEBUG;
    }

    @Override
    protected List<ReactPackage> getPackages() {
        mCallbackManager = CallbackManager.Factory.create();
        return Arrays.<ReactPackage>asList(
            new MainReactPackage(),
            new RCTLocalePackage(),
            new CodePush(BuildConfig.CODEPUSH_KEY, this, BuildConfig.DEBUG),
            new RNSharePackage(),
            new RNMail(),
            new RNAdMobPackage(),
            new RNMixpanel(),
            new RNGeocoderPackage(),
            new AirPackage(),
            new FabricPackage(null),
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

  @Override
  public ReactNativeHost getReactNativeHost() {
      return mReactNativeHost;
  }
}