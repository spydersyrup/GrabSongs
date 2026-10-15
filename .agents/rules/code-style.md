# GrabSongs Code Style

This project's full engineering guidelines live in `CLAUDE.md` at the repo root. Read that file in full and follow it exactly, it is the canonical source. This file is a condensed summary for quick reference.

## Core objective

Build software that is correct, simple, secure, maintainable, performant, testable, and consistent with the existing codebase. Write the minimum code necessary to implement the required behavior correctly. Before writing code: understand the requirement, inspect existing code, search for existing implementations, identify conventions, determine the smallest change, then implement.

## Correctness first, verified against real code

Read the actual current file before editing it, never rely on assumptions or a prior summary of it. Never claim something works, is fixed, or is tested unless it was actually verified by reading the resulting code or running it.

## Smallest safe change, existing patterns over new ones

Search for an existing helper, bridge slot, or component before writing a new one. This codebase already has established patterns, reuse them:
- One class per metadata provider in `core/metadata/`, returning plain dicts, never raising for an expected failure.
- One `@pyqtProperty` / `@pyqtSlot` on `DownloaderBridge` for everything QML can reach; never a second bridge.
- Cooperative cancellation in `DownloadWorker`, set the flag, never `QThread.terminate()`.
- Reuse the QML components in `qml/` (`LucideIcon`, `PressDepthIconButton`, `TransportButton`, `FilterChip`, `SettingRow`, …) instead of writing near-copies.

Full component/architecture inventory: `DESIGN_SYSTEM.md` (UI) and `CODE_PATTERNS.md` (architecture) at the repo root.

## No magic numbers

Tunable thresholds and constants go in `DEFAULT_CONFIG` (`core/config.py`) or a named property on the window root, never as bare literals scattered through logic.

## Near-zero comments, this is the rule Gemini keeps breaking, read it twice

Write code the way a 25-year-experienced developer would: names carry the meaning, comments are the exception not the default. No section-header comments, no restating what the code does, no comments on empty override bodies, no comment referencing "the fix" or "this task." A comment only survives if it explains a genuinely non-obvious constraint a future reader could not infer from the code itself, and even then keep it to one line. Use code only if necessary, don't add a helper, wrapper, or abstraction the task doesn't actually require.

## Theming is routed, never hardcoded

Every color and font goes through a property on the window root in `qml/GrabSongsMain.qml` (`surfaceCard`, `textPrimary`, `recordRed` / `brandAccent`, `bodyFont`, `monoFont`), never a raw hex literal or a hardcoded font family at a call site. The accent marks small interactive state only; it is never a background or a large fill.

## Dependencies

Fonts and icons are bundled offline; nothing is fetched at runtime. Verify any new dependency against `requirements.txt` and its license before adding it, `AGENTS.md` §25 and §75 both apply.

## Scope discipline

Implement exactly what was asked. Don't bundle unrelated fixes, refactors, or "while I'm here" cleanups into the same change unless explicitly requested. If you find an unrelated problem, report it rather than silently fixing it.
