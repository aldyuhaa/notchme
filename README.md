<p align="center">
  <img src="assets/logo.png" width="96" height="96" alt="NotchMe" />
</p>

<h1 align="center">NotchMe</h1>

<p align="center">
  Transform your Mac's notch into a live, interactive island.<br />
  Now Playing · Battery · Weather · Calendar · Notifications · Extensions
</p>

---

## Requirements

- macOS 14 Sonoma or later
- Xcode 15+
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) — `brew install xcodegen`
- Node.js 18+ (only needed to work on extensions)

---

## Setup

```bash
git clone https://github.com/aldyuhaa/notchme.git
cd notchme
xcodegen generate
open NotchMe.xcodeproj
```

Select the `NotchMe` scheme, choose your Mac as the destination, and hit Run.

> On first launch the app will ask for Accessibility, Calendar, and Location permissions. These are required for the relevant modules to work.

---

## Building a DMG

For a quick unsigned local build:

```bash
./scripts/build-dmg.sh
```

For a signed release, use a Developer ID certificate and notarization credentials. Copy `.env.template` to `.env` and fill in:

```
APPLE_ID=you@example.com
APP_SPECIFIC_PASSWORD=xxxx-xxxx-xxxx-xxxx
TEAM_ID=XXXXXXXXXX
SIGNING_IDENTITY=Developer ID Application: Your Name (TEAMID)
```

Then run:

```bash
./scripts/build-and-release.sh
```

This archives a universal app, bundles a universal runtime, notarizes the DMG, and produces `build/NotchMe.dmg`.

Release and Homebrew packaging notes are in [docs/RELEASE.md](docs/RELEASE.md).

To verify a built app bundle:

```bash
./scripts/verify-universal-build.sh build/NotchMe.app --skip-signature
```

---

## Project structure

```
NotchMe/
  App/              AppDelegate, AppState
  Modules/          Built-in modules (Battery, NowPlaying, Weather, …)
  Settings/         Settings window views
  Utilities/        UpdateChecker, AutoUpdater, helpers
  Views/            CompactView, ExpandedView, IslandWindow
ExtensionHost/      JS runtime, extension manager, bridge
Extensions/         Bundled extensions (pomodoro, whatsapp-web, …)
scripts/            Build & release scripts
```

---

## Extensions

Extensions are JavaScript packages that run inside a sandboxed JavaScriptCore context. Read the full guide in [EXTENSIONS.md](EXTENSIONS.md).

## Credits

Originally based on [SuperIsland by shobhit99](https://github.com/shobhit99/SuperIsland). Rebranded and maintained independently as **NotchMe**.

---

## Updates

NotchMe checks for updates automatically on launch. When a new version is available a dialog appears — click **Update** to download and install without reinstalling.
