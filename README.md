# Harmonix — Unified Multi-Platform Music Downloader

**Harmonix** is a modern, high-performance desktop music downloader with a sleek PyQt6 graphical user interface. It combines the universal multi-streaming service engine of **[freyr-js](https://github.com/miraclx/freyr-js)** with the intuitive, native desktop experience and queue management of **[apmyx-gui](https://github.com/rwnk-12/apmyx-gui)**.

---

## 🌟 Highlights & Key Differences

| Feature | `miraclx/freyr-js` | `rwnk-12/apmyx-gui` | **Harmonix (This Project)** |
| :--- | :---: | :---: | :---: |
| **Interface** | CLI only | PyQt6 GUI | **Modern Dark PyQt6 GUI** |
| **Platforms Supported** | Spotify, Apple, Deezer, YouTube | Apple Music only | **Spotify, Apple Music, Deezer, YouTube & Direct Search** |
| **Account / Token Needed** | Optional | Required (Token + WSL Decryptor) | **None required (Zero configuration needed)** |
| **Audio Matching Engine** | Secondary stream matcher | Direct DRM decryption | **High-speed `yt-dlp` stream extraction** |
| **Audio Formats** | M4A, MP3 | AAC, ALAC, Atmos | **MP3 (320k), M4A (256k), FLAC (Lossless), OPUS** |
| **Lyrics** | Basic / external | Synchronized TTML | **Automatic LRCLIB integration (Synced & Plain LRC)** |
| **Built-in Audio Preview Player** | ❌ No | ✅ Yes | **✅ Yes (Integrated QtMultimedia player)** |
| **Interactive Selection Checklist** | ❌ No | ✅ Yes | **✅ Yes (Pick individual tracks from albums/playlists)** |

---

## ✨ Features

- **Universal Link Auto-Detection:** Paste any URL from Spotify, Apple Music, Deezer, or YouTube. Harmonix automatically identifies the service with a visual badge.
- **Direct Search Exploration:** Don't have a URL? Just type song names, artists, or albums into the search bar to query rich catalog metadata.
- **Interactive Track Picker:** View full album and playlist tracklists with album art thumbnails, duration, and track numbers. Check/uncheck specific songs to download only what you want.
- **Automated Lyrics Engine:** Automatically fetches synchronized (`.lrc` timestamps) and plain text lyrics via [LRCLIB](https://lrclib.net/) and embeds them directly into audio tags.
- **Rich Metadata & HD Artwork:** High-resolution cover artwork (up to 1400x1400) and complete ID3v2 / MP4 / Vorbis tags (Artist, Title, Album, Track/Disc Number, Year, Genre) written via `mutagen`.
- **Live Download Queue:** Monitor concurrent downloads with real-time percentage progress bars, download speed (MB/s), ETA countdown, and status badges.
- **Embedded Preview Player:** Built-in audio playback bar at the bottom to preview downloaded songs instantly without leaving the application.
- **Zero-Config FFmpeg:** Automatically discovers FFmpeg on your system PATH or utilizes the bundled high-performance FFmpeg binary from `imageio-ffmpeg`.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Windows, macOS, or Linux

### 2. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/your-username/harmonix.git
cd harmonix
pip install -r requirements.txt
```

### 3. Launch the Application

```bash
python app.py
```

---

## 📁 Project Structure

```
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── core/
│   ├── config.py               # User settings manager & FFmpeg detector
│   ├── audio_player.py         # Qt preview audio player
│   ├── metadata/
│   │   ├── __init__.py         # Unified MetadataResolver
│   │   ├── detector.py         # URL and service regex detector
│   │   ├── spotify.py          # Spotify embed & oEmbed extractor
│   │   ├── apple_music.py      # Apple Music & iTunes lookup client
│   │   ├── deezer.py           # Deezer API client & search
│   │   ├── youtube.py          # YouTube & YT Music extractor
│   │   └── lyrics.py           # LRCLIB synchronized lyrics client
│   └── downloader/
│       ├── worker.py           # QThread yt-dlp download & postprocessing worker
│       ├── queue_manager.py    # Concurrency control & job dispatcher
│       └── tagger.py           # Mutagen ID3/MP4/FLAC metadata & artwork embedder
└── ui/
    ├── styles.py               # Modern dark/glassmorphic QSS stylesheet
    ├── main_window.py          # Main application window & sidebar navigation
    ├── widgets/
    │   ├── badge.py            # Platform source badge
    │   ├── track_card.py       # Track preview card with artwork thumbnail
    │   ├── queue_item.py       # Active download card with live progress bar
    │   └── player_bar.py       # Docked audio preview player bar
    └── pages/
        ├── search_page.py      # Link parser & track selection page
        ├── queue_page.py       # Active download queue management page
        ├── library_page.py     # Local downloaded library page
        └── settings_page.py    # Quality, format, folder & naming preferences
```

---

## ⚙️ Customization & Settings

Inside the **Settings** tab in the app, you can configure:
- **Download Location:** Choose your music folder.
- **Audio Format:** Choose between MP3, M4A, FLAC, or OPUS.
- **Bitrate:** Choose between 320 kbps, 256 kbps, 192 kbps, or Lossless.
- **File Naming Pattern:** Customize file names using `{artist}`, `{title}`, `{album}`, and `{track}` (e.g. `{artist} - {title}`).
- **Lyrics Options:** Choose whether to embed synced lyrics into tags and/or export separate `.lrc` files alongside the song.

---

## 📜 License
Licensed under the [Apache License 2.0](LICENSE).
