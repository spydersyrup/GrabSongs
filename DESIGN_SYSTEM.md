# CassetteCat — Design System

As-built component catalog for the `app/` module (Owned Device theme). This documents what exists in source today, file and line references included, so a future change can match the established pattern instead of inventing a new one. Product/flow-level context lives in `DESIGN.md`.

---

## 1. Color Tokens

Base literals — `ui/theme/Color.kt`:

| Token | Hex | Role |
|---|---|---|
| `RecordRed` | `#C23B30` | Default accent value (see `ThemeAccent.RECORD_RED`) |
| `Background` | `#000000` | App background |
| `Surface` | `#1C1A18` | Cards, panels, now-playing bg |
| `SurfaceVariant` | `#262320` | Secondary surface |
| `Silver` | `#C4C4C0` | Control bodies, `primary` |
| `SilverDim` | `#6E6C68` | Muted control tone, `secondary`/`outline` |
| `TextPrimary` | `#F5F0EC` | Primary text |
| `TextSecondary` | `#A8A29A` | Secondary/muted text |
| `OnRecordRed` | `#000000` | Content drawn on top of an accent fill |

`CassetteCatTheme` (`ui/theme/Theme.kt`) builds a single `darkColorScheme()` from these, plus a user-selected `ThemeAccent` (6 presets + custom hex) mapped onto `tertiary`/`error`, and an AMOLED toggle that swaps `background`/`surface`/the `surfaceContainer*` ladder for near-black variants. **Never reference the literals above directly at a call site** — always go through `MaterialTheme.colorScheme.*`, since accent/AMOLED are runtime-swappable and Minimal theme (deferred) depends on this indirection.

Call-site convention: `tertiary` = the accent, for small interactive elements only (active states, playing indicators, outlines, icons) — never a background or large fill. `primary`/`secondary` = silver neutrals, used for default chrome (buttons, icons) precisely because Material3 defaults `Button`/`FAB` fills to `primary`, and Record Red must never be a default fill color.

`surfaceContainerLow` is the standard card/section background (`SettingsSection`, sheet backgrounds); `outlineVariant` at `0.35–0.4` alpha is the standard hairline border/divider.

---

## 2. Typography

`ui/theme/Type.kt` — `createAppTypography(AppFontFamily)` builds the full Material3 `Typography` scale (`displayLarge` down to `labelSmall`, 13 styles) from one user-selected `AppFontFamily`. All styles share one `FontFamily` and one `scale`/`tracking` pair — pixel/mono-style fonts (Silkscreen, Monocraft, VT323, IBM Plex Mono, system mono) get a slightly compressed scale (0.94–0.96×) and tighter tracking to compensate for wider glyphs; proportional fonts use `1.0×` / `0.sp`.

9 selectable families (`AppFontFamily` enum): Space Grotesk (app default), IBM Plex Sans, IBM Plex Mono, Silkscreen, VT323, Monocraft, System Default/Serif/Mono. A parallel `LyricsFontFamily` enum (9 options) controls lyrics-view typography independently. Always read `MaterialTheme.typography.*` at call sites, never a raw `TextStyle` literal, so the family swap propagates app-wide.

Fixed usage conventions seen across the app (not enforced by the type system, just consistent in practice):
- `bodyLarge` / `bodyMedium` (title/subtitle) — the standard two-line row pattern (`NavigationRow`, `ToggleRow`, `ActionRow`, `ServerRow`, song rows).
- `labelMedium` + `1.2.sp` letter-spacing + `.uppercase()` + `tertiary` color — section headers (`SettingsSection` title).
- IBM Plex Mono specifically (not the user font setting) — technical readouts: track times, EQ dB values, anything meant to read as a device display rather than app copy.

---

## 3. Motion

`ui/navigation/MechanicalTransitions.kt` — the only transition spec used for cross-screen navigation, both the outer and inner (Now Playing) `NavHost`s:
- `TRANSITION_MS = 220`
- `SmoothEasing = CubicBezierEasing(0.42f, 0f, 0.58f, 1f)`
- Enter: slide in from ±¼ screen width + fade in. Exit: slide out to ±¼ screen width + fade out. Forward navigation slides from the right; back navigation (`popEnter`/`popExit`) reverses direction.

No spring/bounce/overshoot easing anywhere in navigation, by design — panels move like mechanical parts, not UI chrome.

Micro-interaction motion (separate from navigation, used on individual controls):
- **Press-depth**: `tween(80, LinearEasing)` animating a `Dp` offset/elevation pair — the shared physical-button feel. See §4.
- `hapticClick(onClick)` (`ui/util/HapticClick.kt`, referenced by nearly every tappable) wraps a click lambda with a haptic tick — the standard way any control fires touch feedback; raw `onClick` lambdas without it are the exception, not the rule.
- `tapScale(onClick)` modifier — a lighter-weight press-scale used on list rows/cards (`NavigationRow`, `ToggleRow`, `ActionRow`, `ServerRow`, `GenreCard`/`FolderCard` corner icons) where full press-depth physics would be excessive.

---

## 4. Buttons

### TransportButton (`ui/components/TransportButton.kt`)
The primary physical-control button — circular, used for play/pause/skip. Shared by Now Playing's transport row and the mini-player.
- Press state: `MutableInteractionSource` → `collectIsPressedAsState()` drives two `animateDpAsState` values in lockstep — `pressDepth` (0→3dp, offset downward) and `elevation` (5dp→0dp) — so the cap visually sinks and its shadow flattens on press, both over `tween(80, LinearEasing)`.
- Visual: `CircleShape`, gradient cap (`Brush.linearGradient` between `surfaceContainerHigh`/`surfaceContainerLowest`), `shadow(elevation, CircleShape)`, 1dp `outlineVariant` border.
- `accented: Boolean` param — when true (e.g. shuffle/repeat active), border becomes 1.5dp `tertiary` instead of 1dp `outlineVariant`. This is the standard way an "active" toggle-style icon button signals state — a border/tint swap to `tertiary`, not a filled background.
- Icon sized at `size * 0.42f` inside the button's own `size` param (caller-specified, varies: large for the main play button, smaller for skip/shuffle).

### PressDepthIconButton (`ui/components/PressDepthIconButton.kt`)
The general-purpose bare icon button — extends the same press-depth language to all other icon-only controls (16 call sites app-wide, replacing raw `IconButton`). Fixed 48dp touch target, icon offset (not the whole box) shifts 1.5dp down on press via the same `tween(80, LinearEasing)` pattern. No background/border — bare icon only, per the Owned Device icon convention (no colored badge/chip container behind icons).

### Standard Material `IconButton`
Still used directly in a handful of places that don't need press-depth physics (e.g. `ServerRow`'s retry action) — acceptable for low-emphasis inline actions, but `PressDepthIconButton` is the default for anything in a primary control surface (Now Playing, mini-player, headers).

### TextButton
Used for lightweight inline actions (`ServerRow`'s "Disconnect") — no custom wrapper, bare Material3 `TextButton`.

---

## 5. Rows (Settings & List Patterns)

`ui/screens/settings/SettingsComponents.kt` defines the canonical settings-row family — every settings screen composes from these rather than hand-rolling rows:

| Component | Shape |
|---|---|
| `SettingsSection(title?, content)` | Optional uppercase `labelMedium` header (tertiary, 1.2sp tracking) + a `RoundedCornerShape(16.dp)` container (`surfaceContainerLow` fill, 0.5dp `outlineVariant` @ 0.35 alpha border) grouping its rows |
| `NavigationRow(title, subtitle, iconRes, onClick, iconTint)` | leading 20dp icon → title/subtitle column → trailing 16dp chevron-right at 0.45 alpha |
| `ToggleRow(title, subtitle, checked, onCheckedChange, iconRes, ...)` | same leading icon/text layout, trailing `Switch` via `appSwitchColors()`; whole row is tap-scale-clickable (not just the switch), `alpha(0.38f)` when `enabled = false` |
| `ActionRow(title, subtitle, iconRes, onClick, iconTint)` | same layout, no trailing affordance — for rows whose only action is the row tap itself |
| `ServerRow(title, subtitle, config, ...)` | same layout; conditionally renders a retry `IconButton` + "Disconnect" `TextButton` when connected, or the chevron when not |

All five share: 20dp horizontal / 14dp vertical padding, `Icon` at 20dp with `secondary` default tint, 18dp icon-to-text spacer, `bodyLarge` title / `bodyMedium` `onSurfaceVariant` subtitle. `SettingsDivider` (24dp inset `HorizontalDivider`, `outlineVariant` @ 0.4 alpha) separates rows within a section when needed.

`appSwitchColors()` — the one shared `SwitchColors` spec app-wide: checked thumb/border = `tertiary`, checked track = `surfaceContainerHighest`, unchecked thumb = `outline`, unchecked track = `surfaceContainerLow`. Every `Switch` in the app should use this rather than Material defaults.

Non-settings row families follow the same leading-icon/text/trailing-affordance shape but are scoped to their own screen (not shared components, by design — each has different data): `SongRow`/`LibrarySongRow`/`SelectableSongRow` (library), `QueueRow` (queue sheet), `MiniPlayerSongRow` (mini-player), `StatSongRow`/`MilestoneRow` (stats), `RadioStationCard`/`NameFilterRow` (radio), `SearchFolderRow`/`SearchArtistRow` (search).

---

## 6. Cards

Grid/shelf cards (`ui/screens/library/LibraryComponents.kt`): `AlbumCard`, `ArtistCard`, `GenreCard`, `FolderCard`, `LikedSongsCard`, `PlaylistCard`, `SmartPlaylistCard`, `SongGridCard` — all share artwork-forward composition (square/circle art + title/subtitle below or overlaid) at consistent grid sizing. `GenreCard`/`FolderCard` add a corner play-icon overlay wired to `.tapScale(onPlay)` for quick-play without opening the detail screen.

`LikedSongsCard` fills with theme tokens (`surfaceContainerHigh`-family gradient), not a hardcoded literal — this was a fix applied earlier in the project specifically because a raw gradient literal violated the "no hardcoded theme colors" rule.

Rule of thumb enforced across cards: don't wrap content in a `Card`/container purely for grouping if the fill is only barely distinguishable from the background — that renders as an invisible wrapper. Cards need a real material difference (elevation, a visibly different `surfaceContainer*` step, or actual artwork) to justify existing as a card rather than bare content on the background.

Other card-shaped composables are screen-local rather than shared, since their content differs enough that a shared abstraction would need heavy parameterization: `HomeSongCard`, `RadioStationCard`/`RadioFilterCategoryCard`, `SearchAlbumCard`/`TopResultSpotlightCard`/`SearchGenreTile`, `RankedCard` (stats), `PermissionCard`/`InfoCard` (onboarding/about), `PresetChip`/`CustomPresetChip` (equalizer), share-sheet preview cards (`SongSharePreviewCard`, `LyricSharePreviewCard`, `LyricQuoteCard`, `ListeningRecordPreviewCard`).

---

## 7. Sheets

Every bottom sheet in the app is a Material3 `ModalBottomSheet`. Two patterns coexist:

**`FullOpenBottomSheet(onDismiss, content)`** (`ui/screens/nowplaying/NowPlayingSheets.kt:70`) — the preferred shared wrapper: `rememberModalBottomSheetState(skipPartiallyExpanded = true)` + `ModalBottomSheet`. Always opens fully expanded, no half-open resting state. Used by `NowPlayingActionsSheet`, `PlaybackSpeedSheet`, `ListeningRoomSheet`, `SongCreditsSheet`, `AudioOutputSheet`, `ScreenshotSuggestionSheet`, `NowPlayingGoToSheet`, `SleepTimerPickerSheet`, and (after a recent migration) `LrcLibSearchSheet`. New sheets should use this wrapper rather than calling `ModalBottomSheet` directly, unless there's a specific reason to allow partial expansion.

**Direct `ModalBottomSheet` calls** — sheets predating the shared wrapper or with bespoke sizing needs, own their `sheetState` inline: `SongTagEditorSheet`, `PlaylistNameSheet` (`PlaylistDetailScreen.kt`), `PlaylistCoverPickerSheet`, `PlaylistPickerSheet`/`SongOptionsSheet` (`LibrarySheets.kt`), `ListeningRecordShareSheet`/`LyricShareSheet`/`ScreenshotShareSheet` (share-card sheets — bespoke because they host a canvas-render preview, not a list).

Close pattern: on a selection/confirm action, call `onDismiss()` directly — the sheet owns its own dismiss-animation via `sheetState`, callers don't manually drive `sheetState.hide()` before calling back (this was standardized during the `LrcLibSearchSheet` migration to `FullOpenBottomSheet`, which doesn't expose its internal `sheetState` to the caller at all).

**Known inconsistency**: `EqualizerScreen`'s "Save Preset" flow uses `AlertDialog` instead of a bottom sheet — the one place a modal dialog is used where the established pattern elsewhere is a sheet. Flagged in a prior review, not yet reconciled; treat as a known gap rather than a pattern to copy.

`AlertDialog` usage elsewhere is for genuine short yes/no confirmations (destructive actions, permission explainers) — that split (sheet for anything with content/options, dialog for a single confirm/cancel decision) is the implicit rule, EqualizerScreen's save-preset dialog is the outlier since it takes text input.

---

## 8. Tabs & Segmented Controls

- **Bottom nav** (`BottomNavBar.kt`) — 5 fixed top-level tabs (Home/Library/Radio/Search/Settings), selection derived from route via `parentTabRoute()` so nested detail screens still highlight their parent tab.
- **Library tabs** — Songs/Artists/Albums/Genres/Folders/Playlists, `HorizontalPager`-backed (`LibraryScreen.kt`), with a `hasSyncedDefaultPage` one-time-correction guard so a configured default page doesn't fight the pager's own state restoration.
- **Now Playing inner tabs** (`LyricsQueueToggleRow`, `NowPlayingControls.kt:181`) — Lyrics/Queue toggle, styled as a segmented pill pair rather than Material `TabRow`, consistent with the "device face" framing (physical-feeling toggle, not a web-style tab strip).

---

## 9. Chips & Pills

Small rounded-capsule elements for filters, status, and inline stats — visually similar but scoped per-screen rather than a single shared composable:
- `ActiveFilterChip` / `NameFilterRow` (radio filters)
- `SearchArtistChip` (search)
- `PresetChip` / `CustomPresetChip` (equalizer preset selector)
- `ShareActionPill` (share sheet action bar)
- `ListeningRoomStatusPill` (connection status indicator)
- `LyricsSyncOffsetPill` (lyrics sync offset readout, IBM Plex Mono per the technical-readout convention in §2)

Shared shape language even without a shared composable: `RoundedCornerShape` (typically 50%/pill), `tertiary`-tinted when active/selected, `surfaceContainer*`-tinted when inactive — same active/inactive color logic as `TransportButton`'s `accented` flag, just applied to a pill instead of a circle.

---

## 10. Icons

- **Library**: Lucide (`com.composables:icons-lucide-android`), referenced via generated `R.drawable.lucide_ic_*` resources.
- **Style**: bare icon only, no colored badge/chip container behind it — thin-line geometric style is meant to read as technical/neutral, not playful. Any new icon usage should follow this (no circular tinted backgrounds, no filled badge wrappers) unless it's specifically a `TransportButton`/`PressDepthIconButton`-style physical control, which gets its container from the button treatment itself, not from icon styling.
- **Standard sizes**: 20dp (settings-row leading icons), 16dp (trailing chevrons, at 0.45 alpha), 48dp touch target for `PressDepthIconButton` (icon itself smaller, centered). `TransportButton` scales its icon to `size * 0.42f` of the button's own caller-specified size.
- **Tint defaults**: `secondary` (silver-dim) for default/inactive icons, `tertiary` (accent) for active/selected states, `onSurfaceVariant` at reduced alpha for de-emphasized trailing affordances (chevrons).

---

## 11. Press-Depth Physics (Core Tactile Language)

The single unifying interaction idea across the whole control surface, described once here since §4 and §9 both reference it: any element meant to feel like a physical control depresses and its shadow deepens/flattens on touch, using the same `tween(80, LinearEasing)` timing everywhere it appears:

| Element | What animates |
|---|---|
| `TransportButton` | Cap offset (0→3dp) + shadow elevation (5dp→0dp) |
| `PressDepthIconButton` | Icon offset only (0→1.5dp) |
| `FaderThumb`/`FaderTrack` (seek bar, `NowPlayingControls.kt`) | Thumb grows + shadow deepens + `tertiary` accent appears while `dragPositionMs != null` |

This is the load-bearing visual metaphor for "industrial-design skeuomorphism, not glossy iOS skeuomorphism" from CLAUDE.md — real depth/press feedback, not gloss/shine. Any new primary control (a future rotary scrubber, new transport action, etc.) should extend this same offset+shadow language rather than introducing a different feedback style (e.g. scale-bounce, color-flash).

---

## 12. Known Inconsistencies (do not silently copy these)

- `EqualizerScreen`'s Save Preset flow uses `AlertDialog` instead of the sheet pattern (§7).
- Smart Playlist tiles use hardcoded neon gradient literals instead of theme tokens — a theming-system violation flagged in review, not yet fixed.
- "8-bit Arcade" / "Retro CRT Terminal" / "Pixel" font-option naming in Customization predates the Owned Device direction and reads as a different design language; not corrected yet.
- Gesture detectors (`ShakeDetector`, `FlipDetector`, `ProximityWaveDetector`, `data/device/`) duplicate sensor-lifecycle and proximity-check logic across three independent classes rather than sharing a base — a known duplication, not a pattern to replicate in a fourth detector.
- 4 separate skip-cooldown implementations (shake, proximity-wave, widget, `SequentialNavigationPlayer`) have drifted to different cooldown values — if adding a fifth skip-triggering surface, check these first rather than inventing another constant.
- Settings/About/Privacy row icon tints (21 hex literals across `SettingsScreen.kt`, `AboutLegalScreen.kt`, `PrivacyScreen.kt`) are a deliberate per-category rainbow scheme — Customization is blue, Equalizer is amber, Listening Room/Record are Record Red, etc. — not an oversight. This is a confirmed, intentional exception to §1's "always route through `colorScheme`" rule: collapsing it to theme tokens today would flatten every row to the same 1-2 hues and destroy the at-a-glance categorization these rows are designed around. If the Minimal (grayscale) theme is ever built, it will need to special-case or override these specifically, rather than the swap happening automatically like everywhere else.

---

## 13. Contribution Rule

Before adding a new button, row, card, sheet, or chip: check §4–§10 above for an existing pattern first. Reuse the shared composable (`TransportButton`, `PressDepthIconButton`, the `SettingsComponents.kt` row family, `FullOpenBottomSheet`, `appSwitchColors()`) rather than hand-rolling a visually-similar one-off. If a genuinely new pattern is needed, it should still follow §1 (theme tokens, never literals), §2 (typography scale, never raw `TextStyle`), and §11 (press-depth physics for anything interactive) — and gets added to this document.
