# Build BioLearn Plus as a downloadable Android APK

## What this project is
This is a Capacitor packaging project for BioLearn Plus. It contains the app web assets, Capacitor configuration, backend and SSS1–SSS3 content bank. The native Android project is generated locally using Capacitor CLI, then built with Android Studio.

## Requirements on your computer
- Node.js 20+
- Android Studio (stable)
- Android SDK platform/tools installed through Android Studio
- Internet connection for first-time npm dependencies and Android Gradle dependencies

## Create the Android native project
Open a terminal in this folder and run:

1. `npm install`
2. `npx cap add android`
3. `npm run cap:sync`
4. `npx cap open android`

In Android Studio:
- Wait for Gradle sync.
- Choose Build > Build Bundle(s) / APK(s) > Build APK(s).
- For a release distributable, use Build > Generate Signed Bundle / APK, choose APK, and create/store a signing key securely.
- Android Studio will show the output location. Typical debug APK: `android/app/build/outputs/apk/debug/app-debug.apk`.

## Update app
After changing files under `www`, run `npm run cap:sync`, then rebuild in Android Studio.

## Backend endpoint
The app needs your deployed backend URL configured in `www/api-client.js` where `API_BASE` is declared. It is currently localhost placeholder, so online account sync will not work from phones until you set the public HTTPS backend origin and redeploy the backend.

## Offline scope
Current PWA service worker caches the app shell. This does not yet provide robust offline-first lesson database or syncing. To support reliable offline access, the app should bundle lesson JSON into local storage/SQLite and queue progress changes for sync.

## Status / limitation
The native Android project and APK are not prebuilt in this delivery: this environment lacks Android SDK/Gradle and cannot reach npm registry to install Capacitor packages. This is a configured Capacitor source package ready for native project generation/build on a machine with Android Studio and internet. It is not yet a signed installable APK.
