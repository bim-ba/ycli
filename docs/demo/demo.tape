# termtosvg recording source (attempted; see note below)
#
# termtosvg WAS installed (uv tool install termtosvg), but the recorded SVG
# captured near-empty output (PTY flushing issue with uv run inside termtosvg).
# The committed docs/assets/demo.svg is a hand-authored static terminal SVG
# that faithfully represents the same prompt/output text as demo.sh.
#
# To attempt a live recording (requires a proper TTY):
#   termtosvg docs/assets/demo.svg --command "bash docs/demo/demo.sh" -g 100x30
#
# Or with vhs (if available):
#   Output docs/assets/demo.gif
#   Set Shell "bash"
#   Type "bash docs/demo/demo.sh"
#   Enter
#   Wait+Line 60
