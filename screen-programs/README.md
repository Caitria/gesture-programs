# screen-programs/ — the suite

Three programs that share one machinery: two-hand tracking, pinch grab
with hysteresis, and a smoothed follow so tracker jitter doesn't
become drift. They were rehearsed on a virtual desk first because a
virtual desk can't break anything real.

| Program | Folder | Start with |
|---------|--------|------------|
| Portal | `portal/` | `portal/README.md` |
| Air Desktop | `air-desktop/` | `air-desktop/README.md` |
| Mac Conductor | `mac-conductor/` | `mac-conductor/README.md` + `mac-conductor/GESTURES.md` |

Shared documents, kept at this level because they belong to all three:

- `PLAN.md` — the build record: every version, what the field tests
  broke, and what changed because of it (v3–v7.3 for the desk).
- `FEEDBACK-QUEUE.md` — the standing fix queue. Nothing gets rebuilt
  per complaint; items wait here until a fix round is called. The
  Conductor's round (items F6–F8) is approved and queued.
- `GESTURE-RESEARCH.md` — the survey of what the gestural-control
  world is building, with candidate additions mapped to these
  programs. Kept as a list, deliberately: ideas wait there until
  they're picked on purpose.

On my Mac each program also lives in its own folder (`~/portal/`,
`~/air-desktop/`, `~/mac-conductor/`); the repo mirrors that, one
folder per program under this one.
