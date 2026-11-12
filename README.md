# BioLearn Plus Android packaging project

See `ANDROID_BUILD_GUIDE.md` to generate and build an APK. `www/` contains the app UI; `backend/` contains the FastAPI service; `content/` includes the draft SSS1–SSS3 content bank.

This download is the source project configured for Capacitor, not an APK binary. Native Android scaffold creation/build requires Android Studio + Android SDK + internet on your local computer.


## APK cloud build
A GitHub Actions workflow is included at `.github/workflows/build-apk.yml`. Follow `GITHUB_CLOUD_APK_BUILD.md` to build and download a debug APK artifact from GitHub Actions.
