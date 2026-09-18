Download these skills: /plugin install skill-creator@claude-plugins-official /plugin install superpowers@claude-plugins-official /plugin marketplace add mksglu/context-mode /plugin install context-mode@context-mode /plugin marketplace add openai/codex-plugin-cc /plugin install codex@openai-codex

Install the following Matt Pocock skills locally (grill-with-docs, improve-codebase-architecture, handoff, prototype, setup-matt-pocock-skills, diagnose, prototype).

Notify me when you have a response ready or when you need me to input something. If I click on the notification, I want to be brought to the terminal.

---

## Status (set up by Claude — 2026-06-15)

✅ **Matt Pocock skills (6) installed** to `~/.claude/skills/` (copied from `github.com/mattpocock/skills`):
grill-with-docs, improve-codebase-architecture, handoff, prototype, setup-matt-pocock-skills, diagnose.
(Your list named `prototype` twice → 6 unique skills.) Run `/setup-matt-pocock-skills` once to configure issue tracker + labels before using the others.

✅ **Click-to-terminal notifications wired** via `Notification` + `Stop` hooks in `~/.claude/settings.json`:

- `~/.claude/bin/terminal-notifier.app` (notarized binary, fetched from GitHub — no Homebrew needed)
- `~/.claude/bin/notify-claude.sh` (hook script; `-activate com.apple.Terminal` → clicking the notification focuses Terminal.app)
- Fires when a response is ready and when input/permission is needed. (Detected your terminal as **Terminal.app**.)

✅ **Plugins (5) installed and enabled** (scope: user) via the non-interactive `claude plugin` CLI:

- `skill-creator@claude-plugins-official`
- `superpowers@claude-plugins-official`
- marketplace `context-mode` added from `mksglu/context-mode`
- `context-mode@context-mode`
- marketplace `openai-codex` added from `openai/codex-plugin-cc`
- `codex@openai-codex`

Verified with `claude plugin list`. They load on the next Claude Code session.

✅ **Node.js installed (2026-06-15)** — the `codex@openai-codex` plugin registers `SessionStart`/`SessionEnd`/`Stop` hooks that shell out to `node`, but no Node runtime was present, causing `Stop hook error: /bin/sh: node: command not found`.

- Installed **Node v24.16.0 (LTS "Krypton"), darwin-x64** — official prebuilt tarball from nodejs.org, no Homebrew needed.
- Extracted to `~/.local/lib/nodejs/node-v24.16.0-darwin-x64/`; `node`, `npm`, `npx` symlinked into `~/.local/bin/` (already first on `PATH`, so the codex hooks resolve `node` even in non-interactive `/bin/sh`).
- Verified: `node --version` → `v24.16.0`, `npm --version` → `11.13.0`, and the codex `stop-review-gate-hook.mjs` runs with exit 0. The hook error is gone.
