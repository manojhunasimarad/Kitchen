# Android shell

A single-activity WebView app (`io.github.manojhunasimarad.kitchen`) with no third-party libraries.

- Opens `https://manojhunasimarad.github.io/Kitchen/`. The site's service worker keeps it working offline; if the
  first load fails, `assets/www/index.html` (copied from the repo root by CI) is shown under the same address so
  the saved data is shared.
- Pages outside `/Kitchen` and links the page marks as external open in other apps.
- `window.KitchenAndroid` gives the page `copyText`, `shareText`, `openExternal`, `saveFile` (to Downloads),
  `setDark` (status and navigation bar colours) and `keepAwake`.
- The back button asks the page (`window.kitchenBack()`) to close a sheet or return to Today before leaving.

Build locally with Android Studio, or with Gradle 8.7+ and JDK 17:

```sh
mkdir -p android/app/src/main/assets/www && cp index.html android/app/src/main/assets/www/
gradle -p android assembleRelease
```
