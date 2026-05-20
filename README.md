# Day Detective — Kivy Android App

## Project structure

```
DayDetective/
├── main.py              ← App entry point
├── theme.py             ← All colours, font sizes, spacing
├── widgets.py           ← Reusable UI components
├── store.py             ← Leaderboard persistence (JSON / Android)
├── buildozer.spec       ← Android build config
├── screens/
│   ├── home.py          ← Home screen (animated title, mode cards)
│   ├── game.py          ← Game screen (Standard + Time Attack)
│   └── leaderboard.py   ← Tabbed leaderboard screen
└── assets/
    ├── music.mp3        ← DROP YOUR MUSIC FILE HERE
    ├── icon.png         ← 512×512 app icon
    └── presplash.png    ← 1080×1920 splash screen
```

---

## Step 1 — Test on your Windows PC

### Install dependencies (once)
```
pip install kivy[base] kivymd buildozer
```

### Run the game
```
cd DayDetective
python main.py
```

The window will behave like a phone — resize it tall and narrow
to simulate a mobile viewport. Everything should work including
the leaderboard, both game modes, and music (if music.mp3 is present).

---

## Step 2 — Build the Android APK

Buildozer only runs on **Linux or macOS** (not Windows directly).
You have two options:

### Option A — WSL (Windows Subsystem for Linux) ← recommended
1. Install WSL2 from Microsoft Store (Ubuntu 22.04)
2. Open Ubuntu terminal, navigate to your project:
   ```
   cd /mnt/d/Aditya/Games/DayDetective
   ```
3. Install buildozer dependencies:
   ```
   sudo apt update && sudo apt install -y \
     python3-pip git zip unzip openjdk-17-jdk \
     autoconf libtool pkg-config zlib1g-dev \
     libncurses5-dev libncursesw5-dev libtinfo5 \
     cmake libffi-dev libssl-dev
   pip3 install buildozer cython==0.29.33
   ```
4. Build the APK:
   ```
   buildozer android debug
   ```
   First build downloads Android SDK/NDK (~2 GB) and takes 20-40 mins.
   Subsequent builds take 2-5 mins.
5. The APK appears at:
   ```
   bin/daydetective-1.0-arm64-v8a_armeabi-v7a-debug.apk
   ```

### Option B — GitHub Actions (free cloud build)
1. Push this project to a GitHub repo
2. Create `.github/workflows/build.yml`:
   ```yaml
   name: Build APK
   on: push
   jobs:
     build:
       runs-on: ubuntu-22.04
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-java@v3
           with: { java-version: '17', distribution: 'temurin' }
         - run: pip install buildozer cython==0.29.33
         - run: sudo apt install -y zip unzip autoconf libtool pkg-config
                  zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev
         - run: buildozer android debug
         - uses: actions/upload-artifact@v3
           with: { name: apk, path: bin/*.apk }
   ```
3. Push and the APK appears under Actions → Artifacts — free.

---

## Step 3 — Test on your phone

1. On your Android phone: Settings → Developer Options → Unknown Sources → ON
2. Copy the .apk to your phone (USB cable or Google Drive)
3. Tap it to install and test
4. Play through both modes, check leaderboard, try music

---

## Step 4 — Create your Play Store assets

Before submitting you need:

| Asset          | Size             | Notes                              |
|----------------|------------------|------------------------------------|
| Icon           | 512×512 PNG      | No alpha required; no rounded corners (Google adds them) |
| Feature Graphic | 1024×500 PNG    | Shown at top of store listing      |
| Screenshots    | Min 2, max 8     | Portrait, 1080×1920 recommended    |
| Short desc     | Max 80 chars     | "Guess the day of the week for any date!" |
| Long desc      | Max 4000 chars   | Describe both modes                |

---

## Step 5 — Sign the APK for release

Google Play requires a **signed** release APK (not debug).

```bash
# Generate a keystore (do this once, keep the file safe forever)
keytool -genkey -v -keystore daydetective.keystore \
        -alias daydetective -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
buildozer android release

# Sign it
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
          -keystore daydetective.keystore \
          bin/daydetective-1.0-*-release-unsigned.apk daydetective

# Align it
zipalign -v 4 \
  bin/daydetective-1.0-*-release-unsigned.apk \
  bin/DayDetective-release.apk
```

---

## Step 6 — Submit to Google Play

1. Go to https://play.google.com/console
2. Create a developer account ($25 one-time fee)
3. Create a new app → fill in details
4. Upload `DayDetective-release.apk` under Production or Internal Testing
5. Fill in the store listing (icon, screenshots, descriptions)
6. Complete the content rating questionnaire (this game = Everyone)
7. Set pricing (Free)
8. Submit for review — Google takes 1-3 days

---

## Customisation

- **Music**: Drop any `.mp3` into `assets/music.mp3` — the app picks it up automatically
- **Time limit**: Change `TIME = 120` in `screens/game.py`
- **Date range**: Change `D_START` / `D_END` in `screens/game.py`
- **Lives**: Change `LIVES = 3` in `screens/game.py`
- **Colours**: Edit `theme.py` — every colour in the app comes from there

