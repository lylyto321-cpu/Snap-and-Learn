# Snap & Learn — Android Build Guide

## Prerequisites

Install these tools before building:

```bash
# 1. Java 17 (required to compile Android)
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
java -version   # should show 17.x

# 2. Android Studio
# Download from: https://developer.android.com/studio
# Run the installer, then open Android Studio and complete setup wizard
# Install Android SDK 34 when prompted

# 3. Set ANDROID_HOME
echo 'export ANDROID_HOME="$HOME/Library/Android/sdk"' >> ~/.zshrc
echo 'export PATH="$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## Build & Run (Debug)

```bash
cd "snap-and-learn"

# Sync web assets into Android project
npx cap sync android

# Open in Android Studio
npx cap open android
```

In Android Studio:
1. Wait for Gradle sync to finish
2. Connect an Android phone (enable Developer Mode + USB Debugging) OR create an emulator
3. Press the green ▶ Run button

---

## Build Release APK / AAB for Google Play

### Step 1 — Generate a signing keystore (one-time)

```bash
keytool -genkey -v \
  -keystore snap-and-learn-release.jks \
  -alias snap-and-learn \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

Keep this `.jks` file safe — you need it for every future update.

### Step 2 — Configure signing in Android Studio

In Android Studio:
- Build → Generate Signed Bundle / APK
- Choose **Android App Bundle** (AAB) — required for Google Play
- Select your `.jks` keystore
- Fill in the key alias and passwords
- Choose `release` build variant
- Click Finish

The output `.aab` file is in `android/app/release/`.

### Step 3 — Submit to Google Play

1. Go to [play.google.com/console](https://play.google.com/console)
2. Create a new app
3. Fill in store listing (title, description, screenshots, icon)
4. Upload the `.aab` file under **Production → Releases**
5. Set content rating (Education)
6. Required: add a **Privacy Policy URL** (the app uses camera and internet)
7. Submit for review (~3-7 days for new apps)

---

## App Icon

Replace these files with your own 512×512 icon (PNG):
- `android/app/src/main/res/mipmap-*/ic_launcher.png` (various sizes)
- `android/app/src/main/res/mipmap-*/ic_launcher_round.png`

Easiest method: In Android Studio, right-click `res` → New → Image Asset → choose your 512×512 PNG.

---

## Project Structure

```
snap-and-learn/
├── www/                    ← Web app (HTML/CSS/JS)
│   ├── index.html          ← Full-screen native app
│   └── duolingo.png        ← Sample image for testing
├── android/                ← Generated Android project
│   ├── app/
│   │   ├── build.gradle
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       └── assets/public/   ← www/ is copied here by `cap sync`
│   └── variables.gradle    ← SDK versions
├── capacitor.config.ts     ← App ID, webDir, plugin config
└── package.json
```

## Updating the App

After editing `www/index.html`:
```bash
npx cap sync android    # copies updated web assets into Android project
# Then rebuild in Android Studio or run on device
```
