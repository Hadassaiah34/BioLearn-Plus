# Build BioLearn Plus APK using GitHub Actions (cloud build)

This project now includes `.github/workflows/build-apk.yml`, which builds an Android debug APK in GitHub's cloud build environment.

## Steps to obtain the APK
1. Create/sign into GitHub and create a new repository (choose private if you prefer).
2. Extract this ZIP on your computer.
3. Upload all extracted project files and folders to that repository, preserving the `.github/workflows/build-apk.yml` path. GitHub's web uploader may not show hidden `.github`; easiest is GitHub Desktop or `git`.
4. Commit/push to the `main` branch. Or open the repository's **Actions** tab, select **Build BioLearn Plus Android APK**, and choose **Run workflow**.
5. Wait for the workflow to complete successfully.
6. Open the completed workflow run. Under **Artifacts**, download `BioLearn-Plus-Android-debug-APK`.
7. Extract the artifact; it contains `app-debug.apk`. Transfer it to Android phone and install. Android may ask permission to install apps from that source; only install the APK you built from your own repository.

## What this achieves
It produces an APK for installation/testing. Debug APK is suitable for testing, not Play Store release. A signed release APK/AAB needs a signing key and release workflow setup.

## Backend connection reminder
For accounts, admin content changes, and cross-device sync, update the API endpoint in the frontend's app configuration to your deployed backend's public HTTPS address, and set the backend CORS origins to your app/site origin. The current endpoint placeholder is localhost; a phone cannot reach the developer computer's localhost.

## Offline reminder
This build installs as an Android app. The service worker's app-shell cache does not by itself ensure that lesson content, quizzes, account features, or progress synchronization all work offline. Full offline-first behavior requires local lesson storage and a sync queue.
