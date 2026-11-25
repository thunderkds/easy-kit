#!/usr/bin/env bash
# tests/test_agent_ws_installer_t353.sh — T353: agent-ws as an opt-in installer choice.
#   SC1 no terminal: no question, no script, no lock key, no agent-ws hook entry
#   SC2 Install, Enter at the question: same project as a no-terminal install (AC 2)
#   SC3 Install, y: script copied and hashed in the lock, "agent_ws": "on", 3 entries (AC 3)
#   SC4 Update (no terminal) of an SC3 project: no question, entries once, script refreshed (AC 4, 5)
#   SC5 Update keeps a user's edit of scripts/agent_ws.py (edit-safe, AC 4)
#   SC6 Reinstall of an "on" project pre-selects Yes (D2); Reinstall + n turns it off
#   SC7 plan screen names the choice before Proceed (AC 6)
#   SC8 not Linux: no question (agent-ws is Linux only)
#   SC9 hooks already wired by hand in settings.local.json: a warning on yes
set -u

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)
. "$SCRIPT_DIR/lib/pty.sh"
detach_from_terminal "$0" "$@"

PASS=0
FAIL=0
pass() { PASS=$((PASS + 1)); printf 'PASS: %s\n' "$1"; }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1" >&2; }
check() { if eval "$2"; then pass "$1"; else fail "$1"; fi; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/agent-ws-installer.XXXXXX")
trap 'rm -rf "$WORK"' EXIT INT TERM HUP

FIXTURE="$WORK/kit"
mkdir -p "$FIXTURE"
( cd "$REPO_ROOT" && git ls-files -co --exclude-standard -z | tar --null -T - -cf - ) \
  | tar -xf - -C "$FIXTURE"
git -C "$FIXTURE" init -q
git -C "$FIXTURE" config user.email t@t
git -C "$FIXTURE" config user.name t
git -C "$FIXTURE" add -A
git -C "$FIXTURE" commit -q -m "kit under test"
SETUP="$FIXTURE/setup.sh"
QUESTION='Turn on parallel builds (agent-ws)?'

new_repo() {
  _r="$WORK/$1"
  mkdir -p "$_r"
  git -C "$_r" init -q
  git -C "$_r" config user.email t@t
  git -C "$_r" config user.name t
  git -C "$_r" commit -q --allow-empty -m init
  printf '%s' "$_r"
}
pty_setup() {   # <repo> <answers>
  ( cd "$1" && SUPERVISOR_REPO="file://$FIXTURE" run_in_pty "$2" "sh '$SETUP'" >"$1.log" 2>&1 )
}
notty_setup() {   # <repo> [extra env assignments...]
  _repo=$1; shift
  ( cd "$_repo" && env SUPERVISOR_REPO="file://$FIXTURE" "$@" setsid -w sh "$SETUP" </dev/null >"$_repo.log" 2>&1 )
}
commit_all() { git -C "$1" add -A >/dev/null 2>&1; git -C "$1" commit -q -m "$2" >/dev/null 2>&1; }
entries() {   # <repo> -> number of hook commands naming agent_ws.py in .claude/settings.json
  python3 - "$1/.claude/settings.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(sum("agent_ws.py" in h.get("command", "") for gs in d.get("hooks", {}).values()
          for g in gs for h in g.get("hooks", [])))
PY
}
lock_has() { grep -q "$2" "$1/.claude/harness-lock.json"; }

# Answers for Install: action, CLIs, project type, [agent-ws], Proceed, board.
INSTALL_NO='\n\n\n\n\n\n'
INSTALL_YES='\n\n\n'"y"'\n\n\n'

# ── SC1 — no terminal ─────────────────────────────────────────────────────────
A=$(new_repo sc1)
notty_setup "$A"; RC=$?
check "SC1: no-terminal install exits 0" '[ "$RC" -eq 0 ]'
check "SC1: no agent-ws question without a terminal" '! grep -qF "$QUESTION" "$A.log"'
check "SC1: no scripts/agent_ws.py" '[ ! -e "$A/scripts/agent_ws.py" ]'
check "SC1: no agent_ws lock key" '! lock_has "$A" "\"agent_ws\""'
check "SC1: no agent-ws hook entry" '[ "$(entries "$A")" -eq 0 ]'

# ── SC2 — Install, Enter = No: byte-identical to SC1 ──────────────────────────
B=$(new_repo sc2)
pty_setup "$B" "$INSTALL_NO"; RC=$?
check "SC2: install with Enter exits 0" '[ "$RC" -eq 0 ]'
check "SC2: the question is asked once" '[ "$(grep -cF "$QUESTION" "$B.log")" -eq 1 ]'
check "SC2: Enter means No (no script)" '[ ! -e "$B/scripts/agent_ws.py" ]'
check "SC2: project equals the no-terminal install (files, settings, lock)" \
  'diff -r -x .git "$A" "$B" >/dev/null'

# ── SC3 / SC7 — Install, y ────────────────────────────────────────────────────
C=$(new_repo sc3)
pty_setup "$C" "$INSTALL_YES"; RC=$?
check "SC3: install with y exits 0" '[ "$RC" -eq 0 ]'
check "SC3: scripts/agent_ws.py is a real file" '[ -f "$C/scripts/agent_ws.py" ] && [ ! -L "$C/scripts/agent_ws.py" ]'
check "SC3: the script equals the kit's" 'cmp -s "$C/scripts/agent_ws.py" "$FIXTURE/scripts/agent_ws.py"'
check "SC3: lock records the script" 'lock_has "$C" "\"scripts/agent_ws.py\""'
check "SC3: lock says agent_ws on" 'lock_has "$C" "\"agent_ws\": \"on\""'
check "SC3: three hook entries" '[ "$(entries "$C")" -eq 3 ]'
check "SC3: entries use the kit-owned form" \
  'grep -qF "\\\"\$CLAUDE_PROJECT_DIR\\\"/scripts/agent_ws.py hook-create" "$C/.claude/settings.json"'
Q=$(grep -naF "$QUESTION" "$C.log" | head -n1 | cut -d: -f1)
P=$(grep -naF "Proceed?" "$C.log" | head -n1 | cut -d: -f1)
L=$(grep -naF "agent-ws:" "$C.log" | head -n1 | cut -d: -f1)
check "SC7: question, then the plan line, then Proceed" '[ "${Q:-0}" -gt 0 ] && [ "${L:-0}" -gt "$Q" ] && [ "${P:-0}" -gt "$L" ]'
commit_all "$C" "install with agent-ws"

# ── SC4 — Update keeps it and refreshes the script ───────────────────────────
printf '# kit change for SC4\n' >> "$FIXTURE/scripts/agent_ws.py"
git -C "$FIXTURE" commit -q -am "kit: agent_ws change"
notty_setup "$C"; RC=$?
check "SC4: update exits 0" '[ "$RC" -eq 0 ]'
check "SC4: no agent-ws question on Update" '! grep -qF "$QUESTION" "$C.log"'
check "SC4: script refreshed from the kit" 'cmp -s "$C/scripts/agent_ws.py" "$FIXTURE/scripts/agent_ws.py"'
check "SC4: lock still says on" 'lock_has "$C" "\"agent_ws\": \"on\""'
check "SC4: entries present exactly once each" '[ "$(entries "$C")" -eq 3 ]'
commit_all "$C" "update"

# ── SC5 — a user's edit survives Update ───────────────────────────────────────
printf '# my local tweak\n' >> "$C/scripts/agent_ws.py"
commit_all "$C" "tweak"
notty_setup "$C"
check "SC5: the edit is kept" 'grep -qF "# my local tweak" "$C/scripts/agent_ws.py"'
check "SC5: entries still there" '[ "$(entries "$C")" -eq 3 ]'
git -C "$C" checkout -q -- . 2>/dev/null; git -C "$C" clean -qfd 2>/dev/null

# ── SC6 — Reinstall: pre-selects Yes, and n turns it off ─────────────────────
D=$(new_repo sc6)
pty_setup "$D" "$INSTALL_YES"; commit_all "$D" "install"
pty_setup "$D" '2\n\n\n\n\n\n'   # Reinstall, Enter at every question
check "SC6: Reinstall shows Yes as the default" 'grep -qF "$QUESTION [Y/n]" "$D.log"'
check "SC6: Reinstall + Enter keeps it on" 'lock_has "$D" "\"agent_ws\": \"on\"" && [ "$(entries "$D")" -eq 3 ]'
commit_all "$D" "reinstall on"
printf '# kit change for SC6\n' >> "$FIXTURE/scripts/agent_ws.py"
git -C "$FIXTURE" commit -q -am "kit: agent_ws change 2"
pty_setup "$D" '2\n\n\n\n\n\n'   # Reinstall after a kit change; the user never edited the script
check "SC6: an unedited script is not backed up on Reinstall" '[ -z "$(find "$D/scripts" -name "agent_ws.py.bak-*")" ]'
check "SC6: and it is refreshed" 'cmp -s "$D/scripts/agent_ws.py" "$FIXTURE/scripts/agent_ws.py"'
commit_all "$D" "reinstall after kit change"
pty_setup "$D" '2\n\n\nn\n\n\n'   # Reinstall, n
check "SC6: Reinstall + n removes the entries" '[ "$(entries "$D")" -eq 0 ]'
check "SC6: Reinstall + n drops the lock key" '! lock_has "$D" "\"agent_ws\""'

# ── SC8 — not Linux: never asked ──────────────────────────────────────────────
SHIM="$WORK/shim"; mkdir -p "$SHIM"
printf '#!/bin/sh\necho Darwin\n' > "$SHIM/uname"; chmod +x "$SHIM/uname"
E=$(new_repo sc8)
( cd "$E" && PATH="$SHIM:$PATH" SUPERVISOR_REPO="file://$FIXTURE" run_in_pty "$INSTALL_NO" "sh '$SETUP'" >"$E.log" 2>&1 )
check "SC8: no question when uname is not Linux" '! grep -qF "$QUESTION" "$E.log"'
check "SC8: nothing agent-ws written" '[ ! -e "$E/scripts/agent_ws.py" ] && [ "$(entries "$E")" -eq 0 ]'

# ── SC9 — hand-wired hooks in settings.local.json ────────────────────────────
F=$(new_repo sc9)
mkdir -p "$F/.claude"
printf '{"hooks":{"WorktreeCreate":[{"hooks":[{"type":"command","command":"python3 /x/scripts/agent_ws.py hook-create"}]}]}}\n' \
  > "$F/.claude/settings.local.json"
pty_setup "$F" "$INSTALL_YES"
check "SC9: a warning names settings.local.json" 'grep -qF "settings.local.json" "$F.log"'

printf '\n--- %s passed, %s failed ---\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
