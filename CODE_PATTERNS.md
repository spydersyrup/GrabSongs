# GrabSongs Code Patterns

As-built architecture and code conventions, with file references. `CLAUDE.md` sets the general
engineering rules (DRY, KISS, minimal changes); this catalogs how those rules are actually applied
in this codebase, so new code matches what exists instead of inventing a new shape.

Sibling to `DESIGN_SYSTEM.md`, which does the same for UI.

---

## 1. Layering

Three layers, no more:

```
app.py            process entry: fonts, icons, QML engine, context properties
  bridge.py       the single QObject boundary Python exposes to QML
    core/metadata/    resolve a URL or query to normalised track dicts
    core/downloader/  queue, download, tag
    core/config.py    persisted settings
```

Everything QML can touch goes through one `@pyqtProperty` / `@pyqtSlot` on `DownloaderBridge`
(roughly 40 signals and slots in `bridge.py`). QML never imports Python and never calls a worker
directly.

**Do not** add a second bridge, a facade, or a service layer between `bridge.py` and `core/`.
`bridge.py` already is the boundary.

---

## 2. Metadata Services

One class per provider in `core/metadata/` (`spotify.py`, `apple_music.py`, `deezer.py`,
`youtube.py`, `generic.py`, `lyrics.py`), each exposing `@classmethod`/`@staticmethod` methods that
return `Optional[Dict[str, Any]]` or `List[Dict[str, Any]]`. They never raise for an expected
failure, a provider that can't resolve returns `None` or `[]`.

`MetadataResolver.resolve(query, target_service)` (`core/metadata/__init__.py`) is the only entry
point: detect the provider with `ServiceDetector`, dispatch, and fall back to a cross-provider text
search. Its return shape is always `{"success": bool, ...}` with `error` set on failure, every
caller checks `success` before reading `tracks`.

Normalised track dicts are plain dicts, not dataclasses: `title`, `artist`, `album`, `service`,
`source_url`, `cover_url`, `duration`, `track_number`. Key spelling varies slightly between
providers; the resolver does not reconcile it. Consumers use `.get()` with defaults.

**Adding a provider:** one module, one class, one branch in `resolve()`, and a case in
`detector.py`. Do not special-case a provider anywhere downstream.

---

## 3. Download Queue and Threading

`QueueManager(QObject)` owns the queue and one `DownloadWorker(QThread)` per active job, capped by
`max_concurrent_downloads`. `bridge.py` connects the manager's signals to its own; QML sees only
`bridge.py`'s.

**Cancellation is cooperative and must stay that way.** `QueueManager.cancel_job()` sets a flag;
the worker observes it at its next check and unwinds, reporting through `error_signal`. Never call
`QThread.terminate()`, it kills the thread mid-write and orphans the ffmpeg child process.

The worker has exactly two cancellation points, because yt-dlp gives no other hook:

- `progress_hook` (`worker.py`), which fires ~1×/s during transfer and raises immediately on cancel;
- a flag check before tagging (`worker.py`), because the hook stops firing once transfer ends.

If you add a new phase to `DownloadWorker.run()`, add a cancellation check at its start. A phase
with no check is a phase that cannot be cancelled.

`_process_queue()` is the single place that starts workers and the single place that advances the
queue; every terminal path (`_on_worker_finished`, `_on_worker_error`) ends by calling it. Cancelled
jobs keep their slot until the worker unwinds, releasing it early would start a replacement while
the old job is still writing.

The queue is written to `~/.grabsongs/queue.json` so an unfinished batch survives a restart.
`_persist()` rewrites that file from `job_store` on every add, cancel, finish and failure, keeping
it equal to whatever would still be pending if the app closed right now. An interrupted download is
non-terminal, so it comes back on the next launch and is retried from the start. `restore()` runs
from `QueueManager.__init__` and ignores a missing, corrupt or wrong-shaped file rather than
blocking startup.

**Thread affinity:** `QueueManager` and `bridge.py` live on the GUI thread, and PyQt queues worker
signals to it, so all `job_store` mutation happens on one thread. Keep it that way: a slot that
mutates `job_store` must not run on the worker thread.

---

## 4. Config

`AppConfig.get_instance()` is a class-level singleton. Read with `.get(key, default)`, write with
`.set(key, value)`, `set` persists the whole file immediately, so don't call it in a loop.

Defaults live in `DEFAULT_CONFIG` (`core/config.py`). Add new settings there, not at the call site;
several call sites already repeat the same fallback literal.

The config file is `config.json` next to the repo root, and it is gitignored.

---

## 5. Error Handling

The established idiom is `except Exception` with a `print()` to stdout, around 20 `print()` calls
and 14 bare excepts across `core/` and `bridge.py`. Match it for consistency when adding code near
existing handlers.

It is a weak idiom and the weakest part of this codebase:

- There is no logging, no severity, and no user-visible error surface. A failure that isn't printed
  is invisible.
- `except Exception: pass` (e.g. in `PyCoverImageProvider.requestImage`) hides real errors.
- `worker.py`'s cancel path deliberately reports through `error_signal`, so "cancelled" and "failed"
  share a signal; `QueueManager` distinguishes them by the `cancelled` flag on the job, not by the
  message.

If you are adding user-facing error handling, route it through `job_error` and don't grow the
print-based pattern further.

---

## 6. QML Components

Reuse before creating. These exist in `qml/`:

| Component | Use for |
|---|---|
| `LucideIcon` | any icon (renders the bundled Lucide SVG set from `assets/icons/`) |
| `PressDepthIconButton` | icon-only button with press depth |
| `TransportButton` | transport controls |
| `SettingCard` / `SettingRow` / `SettingButton` / `SettingSwitch` | settings page |
| `FilterChip` | platform/source filter chips |
| `NavItem` | sidebar navigation entries |
| `AppToolTip` | tooltips |
| `VolumeControl` | volume slider |
| `UiConstants.qml` | durations and easing curves (singleton, no colours) |

`GrabSongsMain.qml` is the window root and holds the theme properties; every other component reads
colours and fonts from it. Don't add a new near-duplicate of a component above, and don't introduce
a second icon set.

`ThemeColors.js` is a theme *parser* (theme JSON → colours, plus WCAG contrast helpers), not the
palette. The palette lives in `GrabSongsMain.qml`.

---

## 7. Naming

- Modules `snake_case`, classes `PascalCase`, functions and properties `camelCase` in QML and
  `snake_case` in Python. Both conventions coexist deliberately by language.
- QML properties are `camelCase` (`surfaceCardHover`, `accentButtonText`).
- Theme properties are the domain vocabulary of this UI (`surfaceBase`, `surfaceCard`, `recordRed`).
  `recordRed` is a historical name that no longer matches the terracotta default, renaming it is
  cosmetic and would touch every component, so leave it unless doing a deliberate sweep.

---

## 8. Comments

Near-zero. Default to none. A comment is justified only for a non-obvious why: a constraint, a
platform quirk, a deliberate trade-off. Never restate the code, never narrate a task, never mention
AI tooling.

The cancellation comments in `queue_manager.py` and `worker.py` are the model: each explains why the
obvious alternative is wrong.

---

## 9. Known Inconsistencies (do not silently copy these)

- **`QueueManager.get_instance()` is vestigial.** `bridge.py` constructs `QueueManager(self)`
  directly; only `scripts/smoke_download.py` calls the singleton. Two calls in one process would get
  two queues with separate `job_store`s.
- **`core/downloader/` has no `__init__.py`** while `core/metadata/` does. Imports work because the
  project runs from the repo root, not because the package is declared.
- **`getDownloadedFiles()` still runs on the GUI thread.** It is cheap now, `read_tags()` memoises on
  `(mtime, size)` and the 1s poll no longer calls it, but it is still a full `os.walk` plus a `stat`
  per file. A library index would remove the walk entirely; until then, do not add per-file work to it.
- **Spotify metadata is scraped** from `__NEXT_DATA__` in the embed page. Apple and Deezer use their
  public APIs. A failed scrape now returns an error naming the provider instead of searching for the
  URL text, so the failure is visible, but the scrape itself is still unmaintained.

---

## 10. Tests

`tests/` runs on stdlib `unittest`, offline, with no test runner to install:

```bash
python -m unittest discover -s tests -t .
```

pytest happens to be present in some virtualenvs but is not a declared dependency, so nothing may
rely on it. Tests stub `yt_dlp` and the metadata providers rather than hitting the network, see
`scripts/` for the live checks, which are deliberately outside the suite.

A fix for a real defect should arrive with the test that would have caught it. That covers the
matcher's fallback, the cancellation lifecycle, the tag cache, the naming/duplicate path, and the
provider-failure path; anything added to `core/` needs the same treatment.

---

## 11. Contribution Rule

Before adding a provider, worker phase, bridge slot, or QML component: check §1–§9 for the existing
shape first. Match the existing class-per-provider metadata pattern (§2), keep cancellation
cooperative (§3), add bridge slots rather than a new bridge (§1), reuse the components in §6 rather
than writing near-copies, and bring a test with it (§10). Near-zero comments always (§8).