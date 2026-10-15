# GrabSongs Design Direction

The intent behind the visual system: what it is trying to feel like, and the rules that aren't
mechanical. The actual token values, component geometry, and code references are in
`DESIGN_SYSTEM.md`; this file is not a second copy of them.

## The idea

The interface is a piece of equipment, not a website. It should feel closer to a well-made tool you
own and operate than to a subscription product: soot-black surfaces, one warm accent, controls that
look pressable, and numbers that read like an instrument display.

Restraint is the method. The palette has no glow, no neon, and no gradient used for emphasis, and
there are no shadow tokens, depth comes from stepping surface lightness. Anything decorative has to
justify its own existence against that.

## Rules that aren't derivable from the token table

**Containerless icons.** An icon button has no background and no border at rest. It gains a surface
only on hover or press. A permanent box behind an icon reads as a button-shaped placeholder rather
than an affordance, so this holds for empty states, error states, and row actions alike, not just
for the primary controls.

**Don't wrap content in a container for grouping.** If a fill is only barely distinguishable from
the background behind it, it isn't a container, it's an invisible wrapper, and the content reads
better sitting directly on the surface. Use a border or a real step in lightness if a group needs to
be distinguishable.

**The accent marks state, never mass.** Accent fills small interactive things: active nav items,
playing indicators, focus borders, progress fill. It is never a background and never a large area.
Where an accent does fill something, `accentButtonText` supplies the contrasting text colour for
that specific accent.

**Mono is for instruments, not for emphasis.** Anything that should read as a machine readout
(bitrate, duration, file size, speed, ETA, paths) is `monoFont`. Labels and sentences are not.

**Motion is mechanical.** Parts slide; nothing bounces casually. Layout transitions are fixed
durations. Overshoot easing is reserved for discrete, user-triggered affordances.

**No fake precision.** Nothing invents numbers, states, or capabilities the app doesn't have:
no decorative statistics, no fake terminals, no telemetry that isn't measured.

## Accessibility

Text must meet WCAG AA (4.5:1) against the surface it sits on; icons and control borders must meet
3:1. All three text tokens now pass on every surface in the palette, `textSecondary` at 6.15:1 on
`surfaceCard`, `textMuted` at 4.57:1 on the lightest surface (`surfaceElevated`), which is the
binding constraint.

An earlier version of this document claimed every token passed AA. It did not: `textMuted` was
`#635E57`, which measured 2.42:1–3.10:1 and was applied to 13px body text. It failed as text and,
on `surfaceElevated`, failed 3:1 as an icon tint too.

## Settled

This system is not being redesigned. New screens reuse the existing tokens, fonts, components, and
rules. They follow the existing screens; they do not introduce a new style.

If a genuinely new need appears, a light theme, a second information density, a new control
category, raise it explicitly first. Those are palette-wide or system-wide changes, not local
ones, and a partial version of one is worse than not having it.