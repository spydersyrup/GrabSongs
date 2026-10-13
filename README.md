# GrabSongs — Multi-Platform Music Downloader Service

**GrabSongs** is a standalone, high-performance desktop music downloader service built with an authentic tactile CassetteCat design system. It combines multi-platform metadata scrapers and audio stream extractors into a seamless experience with zero credentials or accounts required.

---

## 🌟 Studied Implementations & Architecture Inspiration

GrabSongs synthesizes architecture and techniques from leading open-source music tools:

- **[miraclx/freyr-js](https://github.com/miraclx/freyr-js)**: Universal multi-service scraping concepts and metadata resolution across streaming providers.
- **[rwnk-12/apmyx-gui](https://github.com/rwnk-12/apmyx-gui)**: Desktop GUI queue management, concurrent workers, and track-selection checklist workflows.
- **[ots-downloader/onthespot](https://github.com/ots-downloader/onthespot)**: Multi-service provider architecture (Spotify, Apple Music, Deezer, YouTube).
- **[spotbye/SpotiFLAC](https://github.com/spotbye/SpotiFLAC)**: Direct track resolution and high-bitrate audio matching without requiring paid accounts.
- **[sunnypatell/sunnify-spotify-downloader](https://github.com/sunnypatell/sunnify-spotify-downloader)**: Playlist tracklist extraction and automated batch job queues.
- **[henriquesebastiao/downtify](https://github.com/henriquesebastiao/downtify)**: Audio tagging, cover art embedding, and clean local library storage patterns.
- **[Shubhamrawat5/apple-playlist-downloader](https://github.com/Shubhamrawat5/apple-playlist-downloader)**: Apple Music storefront and album catalog scraping mechanisms.

---

## ✨ Features

- **Universal Link Auto-Detection:** Paste links from Spotify, Apple Music, Deezer, or YouTube. GrabSongs instantly identifies the provider and extracts track metadata.
- **Direct Catalog Search:** Search tracks directly across Spotify, Apple Music, Deezer, or YouTube without needing URLs.
- **Tactile CassetteCat UI:** Pure Qt Quick / QML interface using the warm dark surface palette (`#0B0A09` to `#282623`), crisp Space Grotesk / IBM Plex typography, and custom tactile controls (`TransportButton`, `PressDepthIconButton`, `FilterChip`).
- **320 kbps MP3 Conversion:** High-fidelity conversion powered by `yt-dlp` and auto-detected system or bundled FFmpeg.
- **Synchronized Lyrics:** Automated fetching of synchronized (`.lrc` timestamps) and unsynced lyrics via [LRCLIB](https://lrclib.net/) embedded directly into ID3 tags.
- **Complete ID3v2 Tagging:** Mutagen-powered tagging for Title, Artist, Album, Year, Track Number, and high-resolution cover artwork.
- **Full Concurrency & Queue Control:** Concurrent background download workers with progress tracking, speed indicators, and failure recovery.
- **Single-Click Native Windows Launcher:** Launch with `GrabSongs.exe`, `run.bat`, or `python app.py`.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Windows 10/11 (or Linux/macOS with Qt 6)
- Dependencies: `pip install -r requirements.txt`

### Running the App

```bash
# Option 1: Double click or run the compiled launcher
GrabSongs.exe

# Option 2: Run via batch script
run.bat

# Option 3: Run directly with Python
python app.py
```

---

## 📁 Repository Structure

```
├── app.py                      # GrabSongs main application entry point
├── bridge.py                   # PyQt6 / QML bridge & models
├── GrabSongsLauncher.cs        # C# source for GrabSongs.exe
├── GrabSongs.exe               # Compiled native Windows launcher
├── requirements.txt            # Python dependencies
├── AGENTS.md                   # AI Coding Agent engineering rules
├── CLAUDE.md                   # Core architecture and style guide
├── GEMINI.md                   # Gemini engineering guidelines
├── DESIGN.md                   # Design tokens & color ladder
├── DESIGN_SYSTEM.md            # Component catalog & interaction specs
├── CODE_PATTERNS.md            # Established codebase patterns
├── CHAT_LOG.md                 # Full chronological development chat transcript
├── core/
│   ├── config.py               # User preferences & FFmpeg auto-detection
│   ├── metadata/               # Multi-platform scrapers (Spotify, Apple, Deezer, YouTube, LRCLIB)
│   └── downloader/             # yt-dlp downloader, queue manager & mutagen tagger
└── qml/
    ├── GrabSongsMain.qml       # Main GrabSongs application shell
    ├── DownloadPage.qml        # Queue & download manager view
    ├── LucideIcon.qml          # SVG vector icon renderer
    └── ...                     # Shared CassetteCat tactile UI components
```

---

## 📜 License

Licensed under the [GNU General Public License v3.0](LICENSE).
