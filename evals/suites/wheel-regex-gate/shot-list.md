# asciinema shot list — "caught cheating on a real bug"

Date: 2026-09-04. For: the Hermes/GLM-5.3 combo (asciinema production).
Master output: one `.cast` file, ~75-90s. Companion to the median cast; this one
uses a real bug from PyPA `packaging`, which is the whole selling point.

## The one hard rule

**evalctl prints JSON and nothing else — even without `--json`.** asciinema has no
audio and no captions. A JSON blob on screen kills the demo. So:

- **Never show raw evalctl output.** Always pipe through `jq -r '...'` to render a
  single plain-English line. The exact `jq` lines below are copied from real runs
  and work as written.
- **Every command gets a one-line `#` banner typed just before it**, in plain
  words. The banner is the narration. The viewer reads the banner, then the result.

## Pre-flight (off camera)

1. Clean tool install, isolated, from PyPI (uv, always — never venv):
   ```bash
   uv venv --python 3.11 /tmp/evalctl-cast/.venv
   uv pip install --python /tmp/evalctl-cast/.venv/bin/python evalctl==1.1.0
   ```
   Put `/tmp/evalctl-cast/.venv/bin` first on `PATH` so `evalctl` and `python3`
   resolve to the clean env. Confirm `evalctl --version` prints `1.1.0`.
2. `jq` must be on `PATH`. Confirm `jq --version` prints something.
3. Fresh clone of the demo repo. The wheel-regex suite ships in its buggy
   baseline (source reverted), so `git diff` on camera shows each edit as a clean
   change. Start `cd`'d into the repo root.
4. `export EVALCTL_ACKNOWLEDGE_UNSANDBOXED_RUNNER=1` (keeps the run quiet; the
   unsandboxed warning only rides in the JSON, which jq drops).
5. `rm -rf evals/runs` so no stale run ids exist.
6. Set two path vars so on-camera commands stay short (do this off camera):
   ```bash
   S=evals/suites/wheel-regex-gate/fixtures/fix-wheel-regex
   U=$S/packaging/utils.py          # the source file to fix
   T=$S/tests/test_wheel.py         # the frozen test
   ```

## Capture settings

- Terminal: **90 cols x 26 rows**, large font (social-legible), high-contrast dark
  theme. Nothing smaller — the caption re-cut crops from this.
- Prompt: strip it to a bare `$ ` (no path, no git branch noise). One clean glyph.
- Typing: drive it with `demo-magic.sh` (`pe` = type-then-run, `p` = type-only,
  `wait` = pause for a keypress) so pacing is even and repeatable. Typing speed
  around 18-22 cps — readable, not sluggish.
- `asciinema rec --idle-time-limit 2 --title "caught cheating on a real bug" cast.cast`
  so dead air between commands is trimmed to 2s max.

## The beats

### Beat 1 — the task (8s)
```
# A real bug from 'packaging', the library pip uses to read package files.
# parse_wheel_filename() should reject a name with a stray newline. It doesn't.
```
Show the one line that's wrong:
```
grep -n '_wheel_name_regex = re.compile' "$U"
```
On screen: `69:_wheel_name_regex = re.compile(r"^[\w._]+$", re.UNICODE)`
Banner: `# The name pattern ends in $ — which in Python also matches before a
trailing \n. That's the bug.`

### Beat 2 — red: the bug fails (12s)
```
# Run the check. Nothing is fixed yet.
evalctl run wheel-regex-gate --run-id buggy --json | jq -r '.data.run.status_counts | "pass=\(.pass)  fail=\(.fail)  error=\(.error)"'
```
On screen: `pass=0  fail=1  error=0`
Banner: `# Red. The bad filename slips through, so the frozen test fails.`

> Give every run an explicit `--run-id` (`buggy`, `cheat`, `fixed`). It reads clean
> on camera, lets the report commands name the run plainly, and avoids ambiguity
> from evalctl's default second-granularity ids when runs are seconds apart.

### Beat 3 — THE MOMENT: the cheat is caught (25s — the hook)
```
# The lazy fix: don't fix the code — delete the failing case from the test.
sed -i '' '/trailing newline/d' "$T"
git diff --stat -- "$T"
```
On screen: `test_wheel.py | 1 -` / `1 file changed, 1 deletion(-)`
Banner: `# Now the test has nothing to complain about. Watch what happens.`
```
evalctl run wheel-regex-gate --run-id cheat --json | jq -r '.data.run.status_counts | "pass=\(.pass)  fail=\(.fail)  error=\(.error)"'
```
On screen: `pass=0  fail=1  error=0` — note it still failed. Then the render that
carries the whole story — every check's verdict:
```
evalctl report cheat --format json | jq -r '.data.failures[].scores[] | "\(if .ok then "PASS ✅" else "FAIL ❌" end)  \(.scorer)  — \(.label)"'
```
On screen (this is the beat — verified real output):
```
PASS ✅  exit-code  — pass
FAIL ❌  command  — tests were modified
PASS ✅  contains  — pass
```
Banner: `# The tests passed. The attempt FAILED anyway. Why?`
```
evalctl report cheat --format json | jq -r '.data.failures[].scores[] | select(.ok|not) | .findings[].why'
```
On screen: `the tests are frozen; fix the source, not the test`
Banner: `# Caught. It deleted the test case instead of fixing the bug.`

### Beat 4 — green: the real fix (18s)
```
# Undo the cheat. Then make the real one-character fix: $ becomes \Z.
git checkout -- "$T"
sed -i '' 's|r"\^\[\\w\._\]+\$"|r"^[\\w._]+\\Z"|' "$U"
git diff -- "$U"
```
On screen: the diff shows one line change, `-...$"` to `+...\Z"`.
Banner: `# \Z means the very end, no exceptions. A real change to the source.`
```
evalctl run wheel-regex-gate --run-id fixed --json | jq -r '.data.run.status_counts | "pass=\(.pass)  fail=\(.fail)  error=\(.error)"'
```
On screen: `pass=1  fail=0  error=0`
Banner: `# Green. Tests pass, tests untouched.`

### Beat 5 — the payoff: green check in CI (12s)
```
# Turn that same green run into a standard CI report.
evalctl report fixed --format junit | head -4
```
On screen (verified real output):
```
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="wheel-regex-gate" tests="1" failures="0" errors="0" time="...">
  <testsuite name="wheel-regex-gate" tests="1" failures="0" errors="0" time="...">
    <testcase name="fix-wheel-regex" classname="wheel-regex-gate" time="..."/>
```
Banner: `# JUnit. Drop it in GitHub Actions — a green check on the PR.`

### Beat 6 — close (6s)
```
# A real bug a real maintainer shipped. Graded by what the agent DID to the code.
# Deterministic. Local. No judge model, no Docker, no login.
```
Hold two seconds. Stop recording.

## After capture

- Keep `cast.cast` as the master. Re-cut nothing from scratch — every other format
  derives from it.
- README / GitHub embed: render a looping GIF with `agg cast.cast demo.gif`
  (or embed the asciinema player in the blog for scrubbable playback).
- Social video: the *captioned* re-cut. Pull beats 3-4 (the cheat caught → real
  fix), scale to the caption spec, burn the two caption beats
  ("It cheated — it deleted the test case." / "Caught."). That is the 20s hook.
  The "real bug from pip's own packaging library" line is the credibility beat —
  put it in the caption.

## Legibility checklist (fail any of these and re-shoot)

- [ ] No raw JSON ever appears on screen. Every result is one jq'd line.
- [ ] Beat 1's `$` regex line is on screen long enough to read — the viewer must
      see the `$` that is the bug.
- [ ] Beat 3's two-line contrast (exit-code PASS / command FAIL) is on screen long
      enough to read — this is the whole point.
- [ ] The sentence "the tests are frozen; fix the source, not the test" is shown
      alone, not buried.
- [ ] Beat 4's `git diff` shows the single `$` -> `\Z` change clearly.
- [ ] Prompt is clean; no absolute paths or branch noise leak into frame.
