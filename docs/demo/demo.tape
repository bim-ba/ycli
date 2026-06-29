# docs/demo/demo.tape — reproducible source for docs/assets/demo.gif
#
# Regenerate the GIF:
#     vhs docs/demo/demo.tape
# Requires: vhs + ttyd + ffmpeg on PATH (see CONTRIBUTING / README).
# The Hide block below syncs the `mcp` extra up front, so `mcp methods` works and no
# command prints install noise into the recording.
#
# The recording runs the REAL `ycli --help`, renders committed JSON fixtures
# via docs/demo/render.py for the two data commands (no network, no credentials),
# and shows the real `ycli mcp methods` tool list. The shims in docs/demo/bin put
# the real ycli first on PATH inside a Hide block so the demo types plain `ycli ...`.

Output docs/assets/demo.gif

Set Shell bash
Set FontSize 17
Set Width 960
Set Height 900
Set Padding 24
Set TypingSpeed 55ms
Set Theme { "name": "Catppuccin Mocha", "background": "#1e1e2e", "foreground": "#cdd6f4", "cursor": "#f5e0dc", "selection": "#585b70", "black": "#45475a", "brightBlack": "#585b70", "red": "#f38ba8", "brightRed": "#f38ba8", "green": "#a6e3a1", "brightGreen": "#a6e3a1", "yellow": "#f9e2af", "brightYellow": "#f9e2af", "blue": "#89b4fa", "brightBlue": "#89b4fa", "magenta": "#cba6f7", "brightMagenta": "#cba6f7", "cyan": "#94e2d5", "brightCyan": "#94e2d5", "white": "#bac2de", "brightWhite": "#a6adc8" }

# Sync the mcp extra once, set a clean prompt, and put the demo shims first on PATH
# (all off-camera) so the recorded commands run instantly with no install noise.
Hide
Type 'uv sync --extra mcp --dev >/dev/null 2>&1' Enter
Type 'export PATH="$PWD/docs/demo/bin:$PATH"' Enter
Type 'export PS1="❯ "' Enter
Type 'clear' Enter
Show

# Real help output (no creds needed).
Type "ycli --help" Sleep 500ms Enter
Sleep 2.5s

# Fixture-rendered data (committed JSON via render.py — deterministic, offline).
Type "ycli tracker issues get DEMO-42" Sleep 500ms Enter
Sleep 2s

Type "ycli wiki pages get onboarding" Sleep 500ms Enter
Sleep 2s

# Real read-only MCP tool list (no creds, no network).
Type "ycli mcp methods" Sleep 500ms Enter
Sleep 3s
