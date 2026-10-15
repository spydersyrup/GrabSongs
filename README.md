# GrabSongs — Multi-Platform Music Downloader

**GrabSongs** is a standalone, high-performance desktop music downloader. It combines multi-platform metadata scrapers and audio stream extractors into a seamless experience with zero credentials or accounts required.

---

## ✨ Features

- **Universal Link Auto-Detection:** Paste links from Spotify, Apple Music, Deezer, or YouTube. GrabSongs instantly identifies the provider and extracts track metadata.
- **Direct Catalog Search:** Search tracks directly across Spotify, Apple Music, Deezer, or YouTube without needing URLs.
- **Refined Desktop UI:** Pure Qt Quick / QML interface with soot-black surfaces (`#090909` to `#242424`) and a selectable terracotta accent, set in IBM Plex Sans with IBM Plex Mono for technical readouts, and built from reusable controls (`TransportButton`, `PressDepthIconButton`, `FilterChip`).
- **High-Fidelity Audio Conversion:** 320 kbps MP3 / lossless FLAC conversion powered by `yt-dlp` and system FFmpeg.
- **Synchronized Lyrics:** Automated fetching of synchronized (`.lrc` timestamps) and unsynced lyrics via [LRCLIB](https://lrclib.net/) embedded directly into ID3 tags.
- **Complete ID3v2 Tagging:** Mutagen-powered tagging for Title, Artist, Album, Year, Track Number, and high-resolution cover artwork.
- **Full Concurrency & Queue Control:** Concurrent background download workers with progress tracking, speed indicators, and failure recovery.
- **Audio Snippet Preview:** Integrated preview dock to verify tracks before or after downloading.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Linux, macOS, or Windows 10/11
- Dependencies: `pip install -r requirements.txt`

### Running the App

```bash
# Linux / macOS
./run.sh

# Windows
run.bat

# Or directly with Python
python app.py
```

---

## 📁 Repository Structure

```
├── app.py                      # GrabSongs main application entry point
├── bridge.py                   # PyQt6 / QML bridge & models
├── requirements.txt            # Python dependencies
├── run.sh                      # Linux / macOS launcher script
├── run.bat                     # Windows launcher script
├── GrabSongs.desktop           # Linux desktop launcher entry
├── assets/
│   ├── fonts/                  # Bundled IBM Plex Sans & Mono (plus unused alternates)
│   ├── icons/                  # Lucide SVG vector icons
│   ├── grabsongs_icon.png      # Application icon (PNG)
│   └── grabsongs_icon.ico      # Application icon (ICO)
├── core/
│   ├── config.py               # User preferences & FFmpeg auto-detection
│   ├── metadata/               # Multi-platform scrapers (Spotify, Apple, Deezer, YouTube, LRCLIB)
│   └── downloader/             # yt-dlp downloader, queue manager & mutagen tagger
└── qml/
    ├── GrabSongsMain.qml       # Main GrabSongs application shell
    ├── FilterChip.qml          # Platform filter chip component
    ├── LucideIcon.qml          # SVG vector icon renderer
    ├── NavItem.qml             # Sidebar navigation item
    ├── PressDepthIconButton.qml # Tactile depth button
    ├── SettingButton.qml       # Setting action button
    ├── SettingCard.qml         # Setting card container
    ├── SettingRow.qml          # Setting row container
    ├── SettingSwitch.qml       # Setting toggle switch
    ├── TransportButton.qml     # Playback control button
    ├── VolumeControl.qml       # Volume slider popup
    └── ThemeColors.js          # Theme file parser & WCAG contrast helpers
```

---

## 📜 License

**Not yet licensed.** No `LICENSE` file exists in this repository yet, so the code is currently
all rights reserved by default. Pick a license before distributing anything.

This matters here specifically: the icon set in `assets/icons/` is Lucide (ISC) and the bundled
fonts are IBM Plex (OFL). Both allow bundling in a proprietary project with attribution, but neither
license is GPL-3.0, so a GPL-3.0 release would need those bundled assets handled separately.
