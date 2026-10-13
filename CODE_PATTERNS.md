# CassetteCat — Code Patterns

As-built architecture/code conventions for `app/`, with file:line references. `CLAUDE.md` sets the general engineering rules (DRY, KISS, no comments, etc.) — this catalogs how those rules actually get applied in this codebase today, so new code matches existing patterns instead of inventing a new one. Sibling to `DESIGN_SYSTEM.md`, which does the same for UI.

---

## 1. Layering

MVVM + Repository, no additional layers. `ui/screens/<feature>/<Feature>ViewModel.kt` (extends `AndroidViewModel`) → `data/<domain>/<Thing>Repository.kt` → platform APIs (MediaStore, DataStore, OkHttp, Media3). No use-case/interactor layer, no mapper/DTO layer between repository and UI model — repositories expose domain types (`Song`, `Playlist`, etc.) directly, Compose screens read `StateFlow`s off the ViewModel. This is deliberate per CLAUDE.md §10 (avoid Controller→Service→Repository→Interface→Adapter→DTO→Mapper stacking).

`ViewModel` construction: plain `AndroidViewModel(app)` subclasses, no `ViewModelProvider.Factory` boilerplate — `AndroidViewModel` already has a default factory that only needs the `Application`, so repositories are constructed inline in the ViewModel body (`private val repository = PlaybackRepository(app)`), not injected.

**No DI framework** (no Hilt/Koin/Dagger dependency exists in `build.gradle.kts`). Every repository is constructed manually at each call site.

---

## 2. Repository Instantiation — Two Coexisting Patterns

**Plain constructor, instantiated per call site** (the majority pattern — 20+ repositories: `PlaybackRepository`, `AppPreferencesRepository`, `BackupRepository`, `PlaylistRepository`, etc.): `class FooRepository(private val context: Context)`, constructed fresh wherever needed — `remember { FooRepository(context) }` in a composable, or a plain `private val` field in a ViewModel/Service. No shared instance; each construction is assumed cheap (wraps a `DataStore`/file path, does no eager I/O in `init{}`).

**Singleton via `getInstance(context)`** (currently 3 repositories: `SongMetadataOverridesRepository`, `SearchHistoryRepository`, `SongDownloadRepository`): private constructor + `companion object` holding a `@Volatile` instance field, double-checked `synchronized` lock in `getInstance()`. Used specifically where the repository holds in-memory mutable state that must stay consistent across every observer (e.g. metadata overrides read by both the library list and Now Playing simultaneously) — a plain per-call-site instance would let two copies drift out of sync.

**When to use which**: default to the plain-constructor pattern (matches the majority and needs no extra ceremony). Reach for `getInstance()` only when the repository caches mutable state in memory that multiple independent call sites must observe consistently — that was the actual reason the 3 singletons above were converted, not a general "repositories should be singletons" rule.

**Known inconsistency**: `AppPreferencesRepository` is constructed fresh at 20+ call sites (`remember { AppPreferencesRepository(context) }` repeated across nearly every screen file, plus a plain field in every ViewModel). It's backed by DataStore so each instance reads the same underlying store, and this hasn't caused a correctness bug — but it is a lot of duplicated one-line instantiation. Not converted to a singleton because DataStore access itself is already the shared/consistent layer; flagged here as a known duplication, not a bug, in case a future change wants to consolidate it (e.g. a single `remember` higher up passed via `CompositionLocal`, matching the `LocalAppPreferences` pattern in §3 that already exists for the *resolved* preferences value).

---

## 3. Cross-Cutting Reads: `CompositionLocal`

`ui/util/LocalAppPreferences.kt` — `val LocalAppPreferences = compositionLocalOf { AppPreferences() }`, provided once at the root in `MainActivity.kt:61` (`CompositionLocalProvider(LocalAppPreferences provides preferences)`). Used when a deeply-nested composable needs to *read* a resolved preference value (theme accent, font family, etc.) without threading it through every intermediate composable's parameter list. This is for read access to already-resolved state only — it does not replace repository access for anything that writes/mutates (those still go through a repository instance per §2).

---

## 4. Persistence: `sharedJson` + kotlinx.serialization

The standard pattern for small local JSON-backed repositories (`SearchHistoryRepository`, `SongMetadataOverridesRepository`, and others — 20 files reference `sharedJson`): a shared `Json { ... }` configuration object, `@Serializable` data classes for the persisted shape, read/write via `SharedPreferences` or a file path with `sharedJson.encodeToString`/`decodeFromString`. This is the default for "small structured local state" — reach for it before hand-rolling a custom format or introducing Room/SQLite for something that doesn't need querying.

Room/SQLite is used only where the data genuinely needs relational queries (the local library index) — not the default for arbitrary app state.

---

## 5. Concurrency

- **`runCatching`** is the dominant error-handling shape for anything that can fail (183 occurrences across 51 files) — network calls, file I/O, parsing. Wraps the operation, caller inspects `.getOrNull()`/`.onFailure{}`/`.fold{}` rather than a `try/catch` block. Prefer this over raw `try/catch` for a single fallible call.
- **Raw `try/catch`** still appears (~30 files) where multiple distinct exception types need different handling, or at a platform-API boundary that already throws checked-style exceptions (widget providers, `EqualizerController`'s native EQ calls, `RoomAudioServer`'s socket handling). Not a violation of the `runCatching` convention — it's the right tool when `runCatching`'s single-catch-all shape doesn't fit.
- **`Mutex`/`withLock`** — used sparingly, only around a genuine shared-mutable-state race (`SongMetadataOverridesRepository`'s save path, `CoverArtArchiveClient`, `RadioBrowserApiClient`). Not a default wrapper for repository methods; add one only when a concrete concurrent-write scenario exists, not defensively.
- Coroutine scope convention: `viewModelScope` in ViewModels, `CoroutineScope(...)` fields in services/repositories that outlive a single call — no `GlobalScope` usage.

---

## 6. Media3 / Playback-Specific Patterns

- **`ForwardingPlayer` for behavior overrides**: `PlaybackService.kt:682`, `private class SequentialNavigationPlayer(player: Player) : ForwardingPlayer(player)` — wraps the real `ExoPlayer` to override just `hasNextMediaItem`/`hasPreviousMediaItem`/`seekToNext`/`seekToPrevious`/etc. for deterministic index-based navigation, delegating everything else. This is the established technique for "change one behavior, keep the rest of the Player contract intact" rather than reimplementing the `Player` interface or subclassing ExoPlayer internals. Reuse this pattern for any future single-behavior Player override rather than adding more app-side state flags that fight ExoPlayer's own internal state machine (this is exactly the bug class the shuffle/autoplay fix earlier in this project's history ran into — writing `shuffleModeEnabled` on the real player fought ExoPlayer's native gapless auto-advance; `ForwardingPlayer` interception was the fix).
- **Manual queue ordering, not `ShuffleOrder`**: the app owns `currentQueue`/`originalQueue` itself (`PlaybackRepository.kt`) and never delegates shuffle/next/previous to ExoPlayer's native shuffle mode — `shuffleModeEnabled` is read for UI display only, never written to the real player. Any future queue-affecting feature should extend this same app-owned list rather than re-introducing a native-player write.
- **Index resolution across duplicate entries**: `originalIndexOf(currentIndex, currentSong)` (`PlaybackRepository.kt:336`) — when the same song appears more than once in a queue, resolves to the correct *occurrence* by counting how many times that song id has appeared up to `currentIndex` in the current queue, then matching that occurrence count against the original queue. Reuse this helper (or its pattern) for any future index-mapping between two differently-ordered copies of the same queue, rather than a naive `indexOfFirst` (which breaks on duplicate songs).

---

## 7. Naming & Package Conventions

- Package root `in.caffeinelabs.cassettecat` — `in` is a Kotlin reserved word, so every file's `package` line and any cross-package `import` backtick-escapes it: `` package `in`.caffeinelabs.cassettecat ``. Deliberate, confirmed choice — do not rename the package to avoid the escaping.
- File naming: `<Feature>Screen.kt` (composable root), `<Feature>ViewModel.kt`, `<Feature>Repository.kt`, `<Feature>Components.kt`/`<Feature>Sheets.kt` for a screen's smaller composables split out once the main file grows large (e.g. `LibraryComponents.kt`, `NowPlayingSheets.kt`) — the split happens for file-size/navigability reasons, not as a layering rule.
- `internal` visibility is used liberally for composables/functions only meant to be called within their own package (most sub-composables in `*Components.kt`/`*Sheets.kt` files) — `public` is reserved for things genuinely called cross-package (e.g. `TransportButton`, `PressDepthIconButton` in `ui/components/`, meant for reuse app-wide).

---

## 8. Comments

Near-zero. Default to none. The only justified comment is a non-obvious WHY — a hidden constraint, a workaround for a specific platform bug, an invariant a reader could otherwise violate by "cleaning up" the code. Never restate what the code already says, never a comment describing the current task/fix/caller. This has been corrected multiple times over the project's history (see project memory `feedback_no_code_comments`) — treat it as a hard constraint, not a style preference to weigh against other concerns.

---

## 9. Known Inconsistencies (do not silently copy these)

- `AppPreferencesRepository` instantiated fresh at 20+ call sites instead of going through a single shared instance (§2) — works correctly (DataStore-backed), but is duplicated boilerplate.
- `SongMetadataOverridesRepository` does synchronous file I/O in `init{}` on the calling thread, and a disk write failure there is silently swallowed rather than surfaced — flagged in review, not yet fixed.
- `ServiceSettingsRepository` gets re-instantiated across `LocalListeningRoomRepository.kt` rather than reusing one instance, mirroring the same per-call-site pattern as `AppPreferencesRepository`.
- `CoverArtArchiveClient`'s query-building and `extractAudioFormat`'s format-literal list both have small internal duplication not yet consolidated.
- Gesture detectors (`ShakeDetector`, `FlipDetector`, `ProximityWaveDetector`) each hand-roll their own sensor lifecycle and proximity-check logic instead of sharing a base class.
- 4 independent skip-cooldown constants (shake, proximity-wave, widget, `SequentialNavigationPlayer`) have drifted to different values over time.
- `AlbumArtLoader`/`ArtistImageLoader`/`CoverArtArchiveClient` each keep their own 1440px-capable `LruCache` (48/24/36MB, 108MB combined budget), and the same cache/request size serves both small library-grid thumbnails and near-full-width Now Playing art — a deliberate one-loader-for-everything tradeoff (confirmed via RAM/battery audit, 2026-08-26), not a bug. A real fix would mean giving thumbnails their own smaller-capped request/cache path, which is a bigger diff than the other findings from that audit; left as noted, not applied.

---

## 10. Contribution Rule

Before writing a new repository, ViewModel, or playback-behavior override: check §1–§7 above for the existing shape first. Match the plain-constructor repository pattern unless there's a concrete in-memory-consistency reason for a singleton (§2); use `sharedJson` for small structured local state (§4); use `runCatching` for a single fallible call (§5); extend `ForwardingPlayer`/the app-owned queue rather than writing to ExoPlayer's native shuffle/order state (§6). Near-zero comments always (§8).
