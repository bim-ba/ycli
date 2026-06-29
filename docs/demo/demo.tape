# docs/demo/demo.tape — reproducible source for docs/assets/demo.gif
#
# Regenerate the GIF:
#     vhs docs/demo/demo.tape
# Requires: vhs + ttyd + ffmpeg on PATH (see CONTRIBUTING / README).
#
# The recording runs the REAL `ycli --help` and leak-free baked sample data via
# the shims in docs/demo/bin (no network, no credentials). The shims are put
# first on PATH inside a Hide block so the demo types plain `ycli ...` commands.

Output docs/assets/demo.gif

Set Shell bash
Set FontSize 17
Set Width 960
Set Height 720
Set Padding 24
Set TypingSpeed 55ms
Set Theme { "name": "Catppuccin Mocha", "background": "#1e1e2e", "foreground": "#cdd6f4", "cursor": "#f5e0dc", "selection": "#585b70", "black": "#45475a", "brightBlack": "#585b70", "red": "#f38ba8", "brightRed": "#f38ba8", "green": "#a6e3a1", "brightGreen": "#a6e3a1", "yellow": "#f9e2af", "brightYellow": "#f9e2af", "blue": "#89b4fa", "brightBlue": "#89b4fa", "magenta": "#cba6f7", "brightMagenta": "#cba6f7", "cyan": "#94e2d5", "brightCyan": "#94e2d5", "white": "#bac2de", "brightWhite": "#a6adc8" }

# Set up a clean prompt and put the demo shims first on PATH (off-camera).
Hide
Type 'export PATH="$PWD/docs/demo/bin:$PATH"' Enter
Type 'export PS1="❯ "' Enter
Type 'clear' Enter
Show

# Real help output (no creds needed).
Type "ycli --help" Sleep 500ms Enter
Sleep 2.5s

# Baked, leak-free sample data.
Type "ycli tracker issues get TRACKER-1" Sleep 500ms Enter
Sleep 2s

Type "ycli wiki pages get onboarding" Sleep 500ms Enter
Sleep 2s

# Read-only MCP server banner with real tool names.
Type "ycli mcp start" Sleep 500ms Enter
Sleep 3s
