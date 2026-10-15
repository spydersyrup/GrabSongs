# GrabSongs — Design System

As-built UI catalog for the QML layer. This documents what exists in source today, with file
references, so a future change matches the established pattern instead of inventing a new one.

Product and flow context lives in `DESIGN.md`. Code conventions live in `CODE_PATTERNS.md`.

All values below are defined once on the window root, `qml/GrabSongsMain.qml`. Components read them
by name. **Never hardcode a hex literal at a call site** — add a property to the window root and
read that instead, so an accent swap propagates everywhere.

---

## 1. Surfaces

Shades of soot black. Depth is expressed by a small step in lightness, never by glow or shadow.

| Property | Hex | Role |
|---|---|---|
| `surfaceDeep` | `#090909` | Behind full-bleed artwork |
| `surfaceBase` | `#0E0E0E` | Window background |
| `surfaceInput` | `#141414` | Text inputs, resting |
| `surfaceSidebar` | `#131313` | Expanded nav rail |
| `surfaceDock` | `#151515` | Bottom player dock |
| `surfaceCard` | `#181818` | Cards, rows, list backgrounds |
| `surfaceTag` | `#1B1B1B` | Badges, small chips |
| `surfaceCardHover` | `#1F1F1F` | Row hover |
| `surfaceElevated` | `#242424` | Popovers, selected state |
| `surfaceSelected` | `#242424` | Active nav item |

`surfaceElevated` and `surfaceSelected` are currently the same value. That is intentional for now —
selected state reads as elevated — but it means a future "distinct selection" needs a new token
rather than a reinterpretation.

---

## 2. Text

| Property | Hex | Role |
|---|---|---|
| `textPrimary` | `#F4F1EB` | Titles, primary labels |
| `textSecondary` | `#9E978E` | Artist, album, supporting text |
| `textMuted` | `#938A80` | Disabled, placeholder, de-emphasised |
| `silver` | `#E5E2DC` | Neutral control bodies |
| `silverDim` | `#8C867E` | Muted control tone |

`danger` (`#D65A5A`) and `success` (`#5EA67A`) are the only semantic colours. There is no warning
colour; anything that is neither failure nor success is neutral.

All three text tokens meet WCAG AA (4.5:1) against every surface above. `textMuted` is the binding
one: 4.57:1 on `surfaceElevated`, the lightest surface. Anything dimmer fails, so if you need a
fourth tier of de-emphasis it has to come from size or weight, not lightness.

---

## 3. Borders

| Property | Hex | Role |
|---|---|---|
| `borderSubtle` | `#222222` | Resting hairlines, dividers |
| `borderVariant` | `#2B2B2B` | Card borders, input borders |
| `borderCard` | = `borderVariant` | Alias, kept for card call sites |

Borders are 1px hairlines. They are never used to create emphasis through contrast — emphasis comes
from the accent or from type weight.

---

## 4. Accent

The accent is user-selectable. `accentColorMap` (`GrabSongsMain.qml:27`) holds every preset; the
window resolves it into `recordRed`, `recordRedHover`, `accentText`, and `accentButtonText`.

| Preset | Base | Hover | Text on accent |
|---|---|---|---|
| Terracotta (default) | `#D95D39` | `#E86945` | `#FFFFFF` |
| Tangerine | `#F05423` | `#FA6232` | `#FFFFFF` |
| Pine | `#3D7A5A` | `#4B8F6B` | `#5EA67E` |
| Ochre | `#C88A2E` | `#D99B3D` | `#141312` |
| Linen | `#E4DFD7` | `#F2EDE6` | `#161514` |

`brandAccent`, `brandAccentHover`, and `brandAccentText` alias the resolved accent. Use those;
they survive a future rename of the legacy `recordRed` name.

**Call-site convention:** the accent marks small interactive state — active nav items, playing
indicators, focus borders, progress fill, small icons. It is never a large fill or a background.
`accentButtonText` exists because a filled accent button needs the text colour that contrasts with
*that specific* accent; ochre and linen need dark text, the rest need white.

`recordRed` is a historical name that no longer describes the default (terracotta). Renaming it
would touch every component, so it stands. Do not introduce new uses of the literal name; use
`brandAccent*`.

---

## 5. Typography

Two families, both bundled under `assets/fonts/`:

| Property | Family | Use |
|---|---|---|
| `displayFont` | IBM Plex Sans | Headings, titles |
| `bodyFont` | IBM Plex Sans | Everything else |
| `monoFont` | IBM Plex Mono | Technical readouts only |

`monoFont` is for values that should read as an instrument display and nothing else: bitrate,
duration, file size, transfer speed, ETA, path strings. Never use it for a label or a sentence.

`app.py` registers the bundled TTFs via `QFontDatabase.addApplicationFont` and exposes the resolved
families as the `displayFontFamily` / `bodyFontFamily` / `monoFontFamily` context properties, with a
system-font fallback if a family failed to load. Each theme property falls back to IBM Plex when
its context property is undefined, so QML still renders under a preview harness that sets no context.

---

## 6. Geometry

| Token | Value | Use |
|---|---|---|
| Radius, default | 8 | Cards, inputs, album art |
| Radius, compact | 6 | Chips, buttons, small panels |
| Radius, tight | 4 | Badges, tags, progress bars |
| `albumArtRadius` | 8 | Artwork corners |

Radii of 8 and 6 cover almost every surface; 4 is for small elements. Larger radii are not part of
this system. Do not pill-shape anything — a fully rounded control reads as a different product.

Album art is square with `albumArtRadius`, sized to the layout grid (140×140 in library grid cards,
40×40 in result rows, 44×44 in queue cards).

---

## 7. Controls

Reuse the component, don't rebuild it:

| Component | Geometry | Notes |
|---|---|---|
| `SettingSwitch` | 40×22 | Hardware-style toggle, 1px border |
| `PressDepthIconButton` | configurable `boxSize` (36 common) | Icon-only, press-depth offset, transparent at rest |
| `TransportButton` | circular | Transport controls, accent border when active |
| `FilterChip` | auto | Source filter chips |
| `NavItem` | auto | Sidebar entries |
| `AppToolTip` | auto | Tooltips |

**Containerless icons are the rule, not a style preference.** An icon button has no background and no
border at rest; it gains a subtle surface only on hover or press. A permanent box behind an icon
reads as a button-shaped placeholder. This applies to empty states, error states, and row actions
alike.

**No glow, no neon borders, no gradients used for emphasis, no glassmorphism.** The palette has no
shadow tokens; depth comes from surface lightness steps.

---

## 8. Motion

Durations and easing live in `UiConstants.qml` (a singleton):

| Token | Value |
|---|---|
| `durationFast` | 120 ms |
| `durationStd` | 200 ms |
| `durationEmphasis` | 240 ms |
| `durationOverlay` | 280 ms |
| `easingStd` | `Easing.OutCubic` |
| `easingBounce` | `Easing.OutBack` |

Motion is mechanical, not bouncy. Panels and rails slide as physical parts. Spring and overshoot
easing are reserved for `easingBounce` on discrete, user-triggered affordances — not on layout
transitions. Animation must justify itself by communicating state, hierarchy, or spatial
relationship; see `AGENTS.md` §31.

---

## 9. Icons

`LucideIcon.qml` renders the bundled Lucide SVG set from `assets/icons/`. Use it for every icon.
Do not add a second icon set, and do not substitute text or emoji glyphs for interface icons.

Icons ship with the app; the set is not fetched at runtime.

---

## 10. Known gaps

- **`radius: 19` and `radius: 10/11` still exist** in a few places and are outside the §6 scale.
  Consolidating them is cosmetic and untested against the layouts that use them.
- **The accent map is duplicated in the settings swatch list** (`GrabSongsMain.qml:2412+`), which
  re-declares the base hexes so the swatches can render. Adding a preset means editing both.
- **There is no light theme.** Every surface token is a dark value and the palette has no second
  set. Don't start one without asking; it is a palette-wide change, not a toggle.
- **`onAccentNameChanged` re-assigns every accent property by hand** rather than relying on the
  bindings above it. The bindings are already reactive; the handler is redundant belt-and-braces and
  is a place where the two can drift.