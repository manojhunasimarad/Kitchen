package io.github.manojhunasimarad.kitchen;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentValues;
import android.content.Intent;
import android.content.res.Configuration;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.AlarmClock;
import android.provider.MediaStore;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Calendar;

/**
 * Kitchen From Zero as an Android app.
 *
 * It opens the live GitHub Pages site, so every fix published there reaches the phone without a new APK.
 * The site's service worker keeps the last copy for offline use; if the phone has never loaded the site
 * and is offline, the copy bundled inside the APK is shown under the same address, so saved data is shared.
 * Links to grocery apps and other sites open outside the app.
 */
public class MainActivity extends Activity {
    private static final int PICK_FILE = 4021;
    private ValueCallback<Uri[]> fileCallback;

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == PICK_FILE) {
            if (fileCallback != null) fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    static final String HOME = "https://manojhunasimarad.github.io/Kitchen/";
    static final String HOST = "manojhunasimarad.github.io";
    static final int LIGHT_BG = 0xFFE8ECEC, DARK_BG = 0xFF0F1416, LIGHT_BAR = 0xFFFBFCFB, DARK_BAR = 0xFF172024;

    private WebView web;
    private boolean showingBundled = false;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        boolean night = isNight();
        web = new WebView(this);
        web.setBackgroundColor(night ? DARK_BG : LIGHT_BG);
        setContentView(web);
        setBars(night);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setSupportMultipleWindows(false);
        s.setUserAgentString(s.getUserAgentString() + " KitchenFromZeroApp/1");

        web.addJavascriptInterface(new Bridge(), "KitchenAndroid");
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                try {
                    startActivityForResult(params.createIntent(), PICK_FILE);
                } catch (Exception e) {
                    fileCallback = null;
                    Toast.makeText(MainActivity.this, "No app found to pick a photo", Toast.LENGTH_SHORT).show();
                    return false;
                }
                return true;
            }
        });
        web.setWebViewClient(new Client());

        Reminders.schedule(this);
        if (state != null && web.restoreState(state) != null) { openCheckIfAsked(getIntent()); return; }
        web.loadUrl(wantsCheck(getIntent()) ? HOME + "#check" : HOME);
    }

    static boolean wantsCheck(Intent i) { return i != null && "check".equals(i.getStringExtra("open")); }

    void openCheckIfAsked(Intent i) {
        if (!wantsCheck(i)) return;
        i.removeExtra("open");
        web.evaluateJavascript("window.openCheck ? openCheck() : (location.hash = 'check')", null);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        openCheckIfAsked(intent);
    }

    private boolean isNight() {
        return (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
    }

    @SuppressWarnings("deprecation")
    void setBars(boolean dark) {
        Window w = getWindow();
        w.setStatusBarColor(dark ? DARK_BG : LIGHT_BG);
        w.setNavigationBarColor(dark ? DARK_BAR : LIGHT_BAR);
        View d = w.getDecorView();
        int flags = d.getSystemUiVisibility();
        if (dark) flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR; else flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        if (Build.VERSION.SDK_INT >= 26) {
            if (dark) flags &= ~View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR; else flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        }
        d.setSystemUiVisibility(flags);
    }

    /** Pages on the Kitchen site stay in the app; everything else goes to the phone's apps or browser. */
    boolean stayInApp(Uri u) {
        String scheme = u.getScheme() == null ? "" : u.getScheme();
        String path = u.getPath() == null ? "" : u.getPath();
        return (scheme.equals("https") || scheme.equals("http")) && HOST.equals(u.getHost()) && path.startsWith("/Kitchen");
    }

    void openExternal(String url) {
        try {
            Intent i;
            if (url.startsWith("intent:")) {
                i = Intent.parseUri(url, Intent.URI_INTENT_SCHEME);
                i.setComponent(null);
                i.setSelector(null);
            } else {
                i = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            }
            i.addCategory(Intent.CATEGORY_BROWSABLE);
            startActivity(i);
        } catch (Exception e) {
            Toast.makeText(this, "No app on this phone can open that link", Toast.LENGTH_SHORT).show();
        }
    }

    void loadBundled() {
        try (InputStream in = getAssets().open("www/index.html")) {
            String html = new String(readAll(in), StandardCharsets.UTF_8);
            web.loadDataWithBaseURL(HOME, html, "text/html", "utf-8", HOME);
        } catch (IOException e) {
            web.loadData("<p style='font:16px sans-serif;padding:24px'>Connect to the internet once to load Kitchen From Zero.</p>", "text/html", "utf-8");
        }
    }

    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[16384];
        int n;
        while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        return out.toByteArray();
    }

    class Client extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri u = request.getUrl();
            if (stayInApp(u)) return false;
            openExternal(u.toString());
            return true;
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame() && !showingBundled && stayInApp(request.getUrl())) {
                showingBundled = true;
                loadBundled();
            }
        }

        @Override
        public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
            recreate();
            return true;
        }
    }

    /** Small helpers the page calls as window.KitchenAndroid. */
    class Bridge {
        @JavascriptInterface
        public boolean copyText(String text) {
            ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
            if (cm == null) return false;
            cm.setPrimaryClip(ClipData.newPlainText("Kitchen From Zero", text));
            return true;
        }

        @JavascriptInterface
        public void shareText(String text) {
            runOnUiThread(() -> {
                Intent i = new Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, text);
                try { startActivity(Intent.createChooser(i, "Share")); } catch (Exception ignored) { }
            });
        }

        @JavascriptInterface
        public void openExternal(String url) {
            runOnUiThread(() -> MainActivity.this.openExternal(url));
        }

        @JavascriptInterface
        public String saveFile(String name, String text) {
            String safe = name.replaceAll("[^A-Za-z0-9._-]", "_");
            byte[] data = text.getBytes(StandardCharsets.UTF_8);
            try {
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.MediaColumns.DISPLAY_NAME, safe);
                    v.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
                    v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                    Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                    if (uri == null) return "";
                    try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                        if (out == null) return "";
                        out.write(data);
                    }
                    return "Downloads/" + safe;
                }
                File dir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
                if (dir == null) return "";
                File f = new File(dir, safe);
                try (FileOutputStream out = new FileOutputStream(f)) { out.write(data); }
                return f.getAbsolutePath();
            } catch (Exception e) {
                return "";
            }
        }

        @JavascriptInterface
        public void setDark(boolean dark) {
            runOnUiThread(() -> { setBars(dark); web.setBackgroundColor(dark ? DARK_BG : LIGHT_BG); });
        }

        @JavascriptInterface
        public void setReminders(String json) {
            Reminders.save(MainActivity.this, json);
            boolean on = json.contains("\"on\":true");
            if (on && Build.VERSION.SDK_INT >= 33
                    && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED
                    && !getSharedPreferences(Reminders.PREFS, MODE_PRIVATE).getBoolean("asked", false)) {
                getSharedPreferences(Reminders.PREFS, MODE_PRIVATE).edit().putBoolean("asked", true).apply();
                runOnUiThread(() -> requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS}, 7));
            }
        }

        @JavascriptInterface
        public void addClockAlarm(int hour, int minute, String label) {
            runOnUiThread(() -> {
                ArrayList<Integer> days = new ArrayList<>();
                for (int d = Calendar.SUNDAY; d <= Calendar.SATURDAY; d++) days.add(d);
                Intent i = new Intent(AlarmClock.ACTION_SET_ALARM)
                    .putExtra(AlarmClock.EXTRA_HOUR, hour)
                    .putExtra(AlarmClock.EXTRA_MINUTES, minute)
                    .putExtra(AlarmClock.EXTRA_MESSAGE, label)
                    .putExtra(AlarmClock.EXTRA_DAYS, days)
                    .putExtra(AlarmClock.EXTRA_SKIP_UI, false);
                try { startActivity(i); } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Couldn't open the Clock app", Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void keepAwake(boolean on) {
            runOnUiThread(() -> {
                if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            });
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        web.evaluateJavascript("(window.kitchenBack && window.kitchenBack()) ? 1 : 0", result -> {
            if ("1".equals(result)) return;
            if (web.canGoBack()) web.goBack();
            else finish();
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    protected void onPause() {
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.removeJavascriptInterface("KitchenAndroid");
            web.destroy();
        }
        super.onDestroy();
    }
}
