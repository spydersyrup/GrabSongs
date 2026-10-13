# CassetteCat Code Style

This project's full engineering guidelines live in `CLAUDE.md` at the repo root. Read that file in full and follow it exactly, it is the canonical source. This file is a condensed summary for quick reference.

## Core objective

Build software that is correct, simple, secure, maintainable, performant, testable, and consistent with the existing codebase. Write the minimum code necessary to implement the required behavior correctly. Before writing code: understand the requirement, inspect existing code, search for existing implementations, identify conventions, determine the smallest change, then implement.

## Correctness first, verified against real code

Read the actual current file before editing it, never rely on assumptions or a prior summary of it. Never claim something works, is fixed, or is tested unless it was actually verified by reading the resulting code or running it.

## Smallest safe change, existing patterns over new ones

Search for an existing helper, repository, or component before writing a new one. This codebase already has established patterns, reuse them:
- Shared singletons via a `getInstance(context)` companion object only when a repository caches mutable state multiple observers must see consistently; otherwise a plain constructor per call site is the default (see `CODE_PATTERNS.md`).
- `sharedJson` (kotlinx.serialization) for all persistence, never hand-rolled `org.json` parsing.
- `hapticClick` / `hapticToggle` wrappers for every clickable/toggle interaction, not a bare `onClick`/`onCheckedChange`.
- `FullOpenBottomSheet` for every bottom sheet, not a hand-rolled `ModalBottomSheet`.
- `LocalAppPreferences` (CompositionLocal) for reading app settings inside frequently-recomposed leaf composables (list rows, tappable elements), not a per-composable `AppPreferencesRepository` + live Flow subscription.

Full component/architecture inventory: `DESIGN_SYSTEM.md` (UI) and `CODE_PATTERNS.md` (architecture) at the repo root.

## No magic numbers

Tunable thresholds and constants go in a named `companion object`, never as bare literals scattered through logic.

## Near-zero comments — this is the rule Gemini keeps breaking, read it twice

Write code the way a 25-year-experienced developer would: names carry the meaning, comments are the exception not the default. No section-header comments, no restating what the code does, no comments on empty override bodies (use `= Unit`, not a commented-out block), no comment referencing "the fix" or "this task." A comment only survives if it explains a genuinely non-obvious constraint a future reader could not infer from the code itself, and even then keep it to one line. Use code only if necessary — don't add a helper, wrapper, or abstraction the task doesn't actually require.

## Theming is routed, never hardcoded

Every color and font goes through `MaterialTheme.colorScheme` / `MaterialTheme.typography`, never a raw hex literal or a hardcoded font family at a call site. `Record Red` (`colorScheme.tertiary`) is an accent only, never a background or large fill.

## F-Droid / no proprietary dependencies

No Google Play Services, Firebase, or other closed-source Gradle dependency. No downloadable-font providers that depend on GMS. Fonts are bundled offline as local font resources. Verify any new dependency against this before adding it.

## No Tangara or Rhythm reuse

Both are reference-only. Tangara is aesthetic/architecture inspiration only, never copy its code, schematics, or structure. Rhythm is a competitor app used only as a UX benchmark, never copy its code, layouts, or resources, even when opened for comparison.

## Package and licensing conventions

Package id is `in.caffeinelabs.cassettecat`. Since `in` is a Kotlin reserved keyword, every `package` line and cross-package `import` backtick-escapes it: `` package `in`.caffeinelabs.cassettecat ``. This is deliberate, do not "fix" it. `app/` and `firmware/` are GPL-3.0, `hardware/` is CERN-OHL-S-2.0, flag any dependency whose license is incompatible before adding it.

## Scope discipline

Implement exactly what was asked. Don't bundle unrelated fixes, refactors, or "while I'm here" cleanups into the same change unless explicitly requested. If you find an unrelated problem, report it rather than silently fixing it.
