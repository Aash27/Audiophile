"""
app.py  —  Audiophile  |  Hugging Face Spaces
Full pitch detection + age-adjusted feedback demo.
"""

import gradio as gr
from pitch_utils import detect_pitch_and_note
from feedback import generate_feedback
from instruments import INSTRUMENT_RANGES

# ── Instrument list ──────────────────────────────────────────────────────────
INSTRUMENTS = list(INSTRUMENT_RANGES.keys())
AGE_GROUPS  = ["Child (6-12)", "Teen (13-18)", "Adult (18+)"]

EMOJIS = {
    "Guitar": "🎸", "Piano": "🎹", "Voice": "🎤", "Clarinet": "🎼"
}

# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
/* Cantabile — editorial palette */
:root {
	--cream: #f6f1e6;
	--cream-deep: #ece4d2;
	--paper: #fbf7ee;
	--ink: #1f1a14;
	--ink-soft: #5b5247;
	--border: #d8cfbb;
	--gold: #b8893f;
	--rouge: #8a3a2b;

	--serif: 'Cormorant Garamond', 'Playfair Display', Georgia, serif;
	--sans: 'Inter', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;

	--shadow-paper: 0 1px 0 rgba(255, 255, 255, 0.6) inset, 0 18px 40px -22px rgba(31, 26, 20, 0.18);
	--shadow-frame: 0 0 0 1px var(--border), 0 30px 60px -30px rgba(31, 26, 20, 0.25);
	--radius: 0.5rem;
}

* {
	box-sizing: border-box;
}
html,
body {
	margin: 0;
	padding: 0;
}

body {
	background-color: var(--ink);
	background-image: radial-gradient(var(--ink-soft) 0.05px, transparent 1px);
	background-size: 4px 4px;
	color: var(--cream);
	font-family: var(--sans);
	font-size: 16px;
	line-height: 1.5;
	-webkit-font-smoothing: antialiased;
}

img,
audio,
video {
	max-width: 100%;
	display: block;
}
button {
	font: inherit;
	cursor: pointer;
}
a {
	color: inherit;
}

/* Typography */
h1,
h2,
h3,
.serif {
	font-family: var(--serif);
	color: var(--cream);
	font-weight: 500;
	letter-spacing: -0.01em;
	font-size: 2rem;
	margin: 0;
	padding: 0;
}

#left {
	color: var(--cream-deep);
}

#comma {
	color: var(--gold);
	font-size: 4rem;
}

.serif {
	color: var(--cream);
}

.sans {
	font-family: var(--sans);
}
h1 {
	font-size: clamp(2.6rem, 5.5vw, 4.5rem);
	line-height: 1.05;
}
h2 {
	font-size: 1.875rem;
}
h3 {
	font-size: 1.25rem;
}
.italic,
em {
	font-style: italic;
}

.muted {
	color: var(--ink-soft);
}
.eyebrow {
	font-family: var(--sans);
	text-transform: uppercase;
	/* letter-spacing: 0.22em; */
	font-size: 1rem;
	color: var(--cream);
}
.rule {
	height: 1px;
	background: linear-gradient(to right, transparent, var(--border), transparent);
	margin: 1.5rem 0;
	border: 0;
}
.gold-underline {
	background-image: linear-gradient(var(--gold), var(--gold));
	background-repeat: no-repeat;
	background-size: 100% 2px;
	background-position: 0 100%;
	padding-bottom: 2px;
}
.ornament {
	display: inline-flex;
	align-items: center;
	gap: 0.85rem;
}
.ornament::before,
.ornament::after {
	content: '';
	display: inline-block;
	width: 2.5rem;
	height: 1px;
	background: var(--ink-soft);
	opacity: 0.5;
}
.center {
	text-align: center;
}

/* Containers & surfaces */
.container {
	max-width: 72rem;
	margin: 0 auto;
	padding: 0 1.5rem;
}
.container-narrow {
	max-width: 48rem;
	margin: 0 auto;
	padding: 0 1.5rem;
}

.paper {
	background: var(--ink-soft);
	border: 1px solid var(--border);
	border-radius: var(--radius);
	box-shadow: var(--shadow-paper);
}
.frame {
	background: var(--ink-soft);
	border: 1px solid var(--border);
	border-radius: calc(var(--radius) + 4px);
	box-shadow: var(--shadow-frame);
}

/* Masthead */
.masthead {
	border-bottom: 1px solid var(--border);
	background: var(--ink);
	backdrop-filter: blur(8px);
}
.masthead-inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 1.25rem 1.5rem;
	max-width: 72rem;
	margin: 0 auto;
}
.brand {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	text-decoration: none;
	color: inherit;
}
.brand-mark {
	width: 2.25rem;
	height: 2.25rem;
	border-radius: 999px;
	border: 1px solid var(--border);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-family: var(--serif);
	font-style: italic;
}
.brand-name {
	font-family: var(--serif);
	font-size: 1.25rem;
	padding-bottom: 0;
	line-height: 1;
}
.brand-tag {
	margin-top: 0.25rem;
}

.nav {
	display: none;
	gap: 2rem;
	align-items: center;
	font-size: 0.875rem;
}
.nav a {
	text-decoration: none;
	color: var(--ink-soft);
}
.nav a:hover {
	color: var(--cream);
}
.nav a.active {
	color: var(--cream);
}
.nav a.active span {
	/* gold underline applied via class */
}

.issue {
	display: none;
	text-align: right;
	font-size: 0.75rem;
	color: var(--ink-soft);
}
.issue .serif {
	display: block;
}

@media (min-width: 768px) {
	.nav,
	.issue {
		display: flex;
	}
	.issue {
		display: block;
	}
}

/* Hero */
.hero {
	padding: 1rem;
}
.hero h1 em {
	color: var(--ink-soft);
}
.hero p {
	max-width: 36rem;
	margin: 1.5rem auto 0;
	color: var(--cream);
	font-size: 1.05rem;
}

/* Two-column layout for index */
.layout {
	display: grid;
	grid-template-columns: 1fr;
	gap: 3rem;
	margin-top: 4rem;
}
@media (min-width: 880px) {
	.layout {
		grid-template-columns: 5fr 7fr;
		gap: 3rem;
	}
}

/* Instructions list */
.steps {
	list-style: none;
	padding: 0;
	margin: 0;
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}
.step {
	display: flex;
	gap: 1.25rem;
}
.step-num {
	font-family: var(--serif);
	font-style: italic;
	color: var(--cream-deep);
	font-size: 1.875rem;
	line-height: 1;
}
.step-title {
	font-family: var(--sans);
	font-size: 1.125rem;
	margin-top: 0.25rem;
}
.step-desc {
	margin-top: 0.25rem;
	color: var(--ink-soft);
	font-size: 0.9rem;
	line-height: 1.55;
}

.note {
	margin-top: 2.5rem;
	padding: 1.5rem;
}
.note p {
	margin: 0.5rem 0 0;
	color: var(--cream-deep);
	font-size: 0.9rem;
	line-height: 1.55;
}

/* Form */
.form {
	padding: 2rem;
}
@media (min-width: 768px) {
	.form {
		padding: 2.5rem;
	}
}
.form-head {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	gap: 1rem;
}
.form-head h2 {
	margin-top: 0.5rem;
}
.formats {
	font-family: var(--serif);
	color: var(--cream);
}

.dropzone {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 3rem 1.5rem;
	border: 1px dashed var(--border);
	border-radius: var(--radius);
	color: var(--cream);
	text-align: center;
	cursor: pointer;
	transition:
		background-color 150ms ease,
		border-color 150ms ease;
}
.dropzone:hover {
	background: rgba(216, 207, 187, 0.25);
}
.dropzone.is-drag {
	border-color: var(--gold);
	background: var(--cream-deep);
}
.dropzone input {
	position: absolute;
	opacity: 0;
	pointer-events: none;
}
.dropzone-title {
	font-family: var(--serif);
	font-size: 1.5rem;
	font-style: italic;
}
.dropzone-hint {
	margin-top: 0.5rem;
	color: var(--cream);
	font-size: 0.9rem;
}
.dropzone-cap {
	margin-top: 0.75rem;
	font-size: 0.7rem;
	text-transform: uppercase;
	letter-spacing: 0.22em;
	color: var(--cream);
}

.dropzone .file-name {
	font-family: var(--serif);
	font-size: 1.25rem;
}
.dropzone .file-meta {
	margin-top: 0.25rem;
	font-size: 0.75rem;
	color: var(--ink-soft);
}
.remove-btn {
	background: transparent;
	border: 0;
	padding: 0;
	margin-top: 1rem;
	font-size: 0.7rem;
	text-transform: uppercase;
	letter-spacing: 0.2em;
	color: var(--ink-soft);
}
.remove-btn:hover {
	color: var(--cream);
}

.fields {
	display: grid;
	grid-template-columns: 1fr;
	gap: 1.5rem;
	margin-top: 2rem;
}
@media (min-width: 640px) {
	.fields {
		grid-template-columns: 1fr 1fr;
	}
}
.field {
	display: block;
}
.field-label {
	display: block;
}
.field input,
.field select,
.field textarea {
	width: 100%;
	background: transparent;
	border: 0;
	border-bottom: 1px solid var(--border);
	padding: 0.5rem 0;
	font-family: var(--sans);
	font-size: 1.05rem;
	color: var(--cream);
	outline: none;
	transition: border-color 150ms ease;
	margin-top: 0.25rem;
}
.field textarea {
	resize: none;
	font-size: 1rem;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
	border-color: var(--cream);
}
.field-full {
	grid-column: 1 / -1;
}

.actions {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	margin-top: 2.5rem;
}
.actions .small {
	font-size: 0.75rem;
	font-style: italic;
	color: var(--ink-soft);
}
.btn-primary {
	display: inline-flex;
	align-items: center;
	gap: 0.75rem;
	background: var(--cream);
	color: var(--ink);
	border: 0;
	padding: 0.85rem 1.75rem;
	border-radius: 999px;
	font-size: 0.875rem;
	font-weight: 500;
	transition:
		gap 150ms ease,
		opacity 150ms ease;
}
.btn-primary:hover {
	gap: 1rem;
}
.btn-primary:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.btn-ghost {
	display: inline-flex;
	align-items: center;
	gap: 0.75rem;
	background: transparent;
	color: var(--ink);
	border: 1px solid var(--cream);
	padding: 0.75rem 1.5rem;
	border-radius: 999px;
	font-size: 0.875rem;
	text-decoration: none;
	transition:
		background-color 150ms ease,
		color 150ms ease;
}
.btn-ghost:hover {
	background: var(--cream);
	color: var(--ink);
}

/* Footer */
.footer {
	margin-top: 6rem;
	border-top: 1px solid var(--border);
}
.footer-inner {
	max-width: 72rem;
	margin: 0 auto;
	padding: 2.5rem 1.5rem;
	text-align: center;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;
}
.footer p {
	margin: 0;
	font-size: 0.75rem;
	color: var(--ink-soft);
}

/* Toast */
.toast {
	position: fixed;
	top: 1.5rem;
	left: 50%;
	transform: translateX(-50%) translateY(-1rem);
	background: var(--cream);
	color: var(--ink);
	padding: 0.75rem 1.25rem;
	border-radius: 999px;
	font-size: 0.85rem;
	opacity: 0;
	pointer-events: none;
	transition:
		opacity 200ms ease,
		transform 200ms ease;
	z-index: 50;
	box-shadow: 0 12px 40px -10px rgba(0, 0, 0, 0.35);
}
.toast.show {
	opacity: 1;
	transform: translateX(-50%) translateY(0);
}

/* ============ Feedback page ============ */

.crit-meta {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 0.75rem 1.25rem;
	font-size: 0.75rem;
	color: var(--ink-soft);
	margin-top: 2rem;
}
.crit-meta span.dot {
	opacity: 0.5;
}

.player {
	padding: 1.25rem;
	margin-top: 2.5rem;
}
.player audio {
	width: 100%;
}

.lede {
	font-size: 1.1rem;
	line-height: 1.7;
}
.drop-cap::first-letter {
	font-family: var(--serif);
	float: left;
	font-size: 3.6rem;
	line-height: 0.85;
	padding: 0.35rem 0.6rem 0 0;
	color: var(--ink);
}

.mark-bar {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
	gap: 1rem;
	border-top: 1px solid var(--border);
	border-bottom: 1px solid var(--border);
	padding: 2rem 0;
	margin: 3.5rem 0;
}
.mark-bar .mark-num {
	font-family: var(--serif);
	font-size: 4.5rem;
	line-height: 1;
}
.mark-bar .mark-cap {
	margin-top: 0.25rem;
}
.mark-bar .right {
	text-align: right;
}

.scores {
	list-style: none;
	padding: 0;
	margin: 2rem 0 0;
	border-top: 1px solid var(--border);
}
.score-row {
	display: grid;
	grid-template-columns: 1fr 80px;
	align-items: baseline;
	gap: 1rem;
	padding: 1.25rem 0;
	border-bottom: 1px solid var(--border);
}
@media (min-width: 720px) {
	.score-row {
		grid-template-columns: 4fr 6fr 80px;
	}
}
.score-label {
	font-family: var(--serif);
	font-size: 1.125rem;
}
.score-mid {
	grid-column: 1 / -1;
}
@media (min-width: 720px) {
	.score-mid {
		grid-column: 2 / 3;
	}
}
.score-bar {
	height: 2px;
	background: var(--border);
	width: 100%;
}
.score-bar > span {
	display: block;
	height: 2px;
	background: var(--cream);
}
.score-note {
	margin-top: 0.5rem;
	font-size: 0.85rem;
	font-style: italic;
	color: var(--ink-soft);
}
.score-num {
	font-family: var(--serif);
	font-size: 1.5rem;
	text-align: right;
}

.two-col {
	display: grid;
	gap: 2.5rem;
	margin-top: 4rem;
	grid-template-columns: 1fr;
}
@media (min-width: 720px) {
	.two-col {
		grid-template-columns: 1fr 1fr;
	}
}
.col-list {
	list-style: none;
	padding: 0;
	margin: 1rem 0 0;
	display: flex;
	flex-direction: column;
	gap: 1rem;
}
.col-item {
	display: flex;
	gap: 0.75rem;
}
.col-item .bullet {
	width: 6px;
	height: 6px;
	border-radius: 999px;
	background: var(--cream);
	margin-top: 0.65rem;
	flex-shrink: 0;
}
.col-item.accent .bullet {
	background: var(--gold);
}
.col-item p {
	margin: 0;
	font-family: var(--serif);
	font-size: 1.125rem;
	line-height: 1.4;
}

.exercises {
	display: grid;
	gap: 1.5rem;
	margin-top: 2rem;
	grid-template-columns: 1fr;
}
@media (min-width: 720px) {
	.exercises {
		grid-template-columns: 1fr 1fr 1fr;
	}
}
.exercise {
	padding: 1.5rem;
}
.exercise .num {
	font-family: var(--serif);
	font-style: italic;
	color: var(--ink-soft);
	font-size: 1.875rem;
}
.exercise h3 {
	font-family: var(--serif);
	font-size: 1.125rem;
	margin-top: 0.5rem;
}
.exercise p {
	margin: 0.5rem 0 0;
	color: var(--ink-soft);
	font-size: 0.9rem;
	line-height: 1.55;
}

.crit-foot {
	text-align: center;
	margin-top: 4rem;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 1.5rem;
}

/* Empty state for direct visit to feedback.html */
.empty {
	text-align: center;
	padding: 6rem 1.5rem;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 1rem;
}

/* Listening (loading) state */
.listening {
	text-align: center;
	padding-top: 8rem;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 1rem;
}
.dots {
	display: flex;
	gap: 0.5rem;
	margin-top: 2rem;
}
.dots span {
	width: 8px;
	height: 8px;
	border-radius: 999px;
	background: var(--cream);
	animation: blink 1.2s infinite ease-in-out;
}
.dots span:nth-child(2) {
	animation-delay: 0.18s;
}
.dots span:nth-child(3) {
	animation-delay: 0.36s;
}
@keyframes blink {
	0%,
	100% {
		opacity: 0.25;
	}
	50% {
		opacity: 1;
	}
}

.hidden {
	display: none !important;
}

"""


# ── HTML builders ────────────────────────────────────────────────────────────

def _color(key):
    return {
        "green": "#2f6f3e",
        "red":   "#a13030",
        "blue":  "#1d4ed8",
        "gold":  "#9a5b16",
        "muted": "#475569",
    }.get(key, "#f0ede6")


def render_pitch_html(note, frequency, cents, accuracy, consistency, all_notes):
    """Build the styled pitch-result panel."""
    from feedback import intonation_label, consistency_label, grade_from_accuracy

    tune_str, direction = intonation_label(cents)
    tune_col = _color("green") if direction == "intune" else (
               _color("red") if direction == "sharp" else _color("blue"))

    needle_pct = 50 + max(-47, min(47, cents * 0.94))

    grade = grade_from_accuracy(accuracy)
    grade_col = _color("green") if accuracy >= 80 else (
                _color("gold") if accuracy >= 65 else _color("red"))

    cons_lbl = consistency_label(consistency)
    cons_col = _color("green") if consistency >= 75 else (
               _color("gold") if consistency >= 55 else _color("red"))

    # Note chips
    chips_html = ""
    if all_notes:
        total = sum(c for _, c in all_notes)
        for n, cnt in all_notes:
            pct = cnt / total * 100 if total else 0
            chips_html += (
                f"<span class='chip' style='margin:0.25rem;'>{n} <span style='opacity:.75;font-weight:600;'>{pct:.0f}%</span></span>"
            )
    else:
        chips_html = "<p style='margin:0;color:var(--color-text-muted);font-size:var(--text-sm);'>No additional notes were detected.</p>"

    return f"""
<section class='pitch-card' style='padding:1.5rem;' aria-labelledby='pitch-results-title'>
  <div class='sec-label' style='margin-top:0 !important;'>Pitch analysis</div>
  <h2 id='pitch-results-title' class='sec-title' style='margin-bottom:1rem !important;'>Your recording at a glance</h2>

  <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.9rem;margin-bottom:1rem;'>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-bottom:0.5rem;'>Dominant note</div>
      <div style='font-size:clamp(1.8rem,4vw,2.5rem);font-weight:800;color:{tune_col};line-height:1;'>{note}</div>
      <div style='font-size:var(--text-xs);color:var(--color-text-faint);margin-top:0.35rem;'>Letter notation</div>
    </article>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-bottom:0.5rem;'>Frequency</div>
      <div style='font-size:clamp(1.7rem,4vw,2.3rem);font-weight:800;color:var(--color-text);line-height:1.1;'>{frequency:.1f}</div>
      <div style='font-size:var(--text-xs);color:var(--color-text-faint);margin-top:0.35rem;'>Hz</div>
    </article>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-bottom:0.5rem;'>Intonation</div>
      <div style='font-size:clamp(1.1rem,2vw,1.35rem);font-weight:800;color:{tune_col};line-height:1.2;'>{tune_str}</div>
      <div style='font-size:var(--text-xs);color:var(--color-text-faint);margin-top:0.35rem;'>{cents:+.1f} cents</div>
    </article>
  </div>

  <section class='feedback-card' style='padding:1rem 1rem 1.1rem;margin-bottom:1rem;' aria-label='Pitch meter'>
    <div style='display:flex;justify-content:space-between;gap:0.75rem;flex-wrap:wrap;font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-bottom:0.75rem;'>
      <span>Flat</span><span>In tune</span><span>Sharp</span>
    </div>
    <div style='position:relative;height:0.85rem;background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:999px;overflow:hidden;'>
      <div style='position:absolute;top:0;bottom:0;left:50%;width:2px;background:var(--color-text-faint);transform:translateX(-50%);opacity:.55;'></div>
      <div style='position:absolute;inset:0;background:linear-gradient(90deg, color-mix(in srgb, {tune_col} 12%, transparent), transparent 35%, transparent 65%, color-mix(in srgb, {tune_col} 12%, transparent));'></div>
      <div aria-hidden='true' style='position:absolute;top:-0.25rem;left:{needle_pct:.0f}%;width:0.35rem;height:1.35rem;background:{tune_col};border-radius:999px;transform:translateX(-50%);box-shadow:0 0 0 3px color-mix(in srgb, {tune_col} 18%, transparent);'></div>
    </div>
  </section>

  <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0.9rem;margin-bottom:1rem;'>
    <article class='stat-card' style='padding:1rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;'>
      <div>
        <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);'>Pitch accuracy</div>
        <div style='font-size:var(--text-xs);color:var(--color-text-faint);margin-top:0.25rem;'>Overall tuning score</div>
      </div>
      <div style='font-size:clamp(1.4rem,3vw,2rem);font-weight:800;color:{grade_col};'>{accuracy:.0f}%</div>
    </article>
    <article class='stat-card' style='padding:1rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;'>
      <div>
        <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);'>Consistency</div>
        <div style='font-size:var(--text-xs);color:var(--color-text-faint);margin-top:0.25rem;'>Stability across the take</div>
      </div>
      <div style='font-size:clamp(1.2rem,2.8vw,1.7rem);font-weight:800;color:{cons_col};'>{cons_lbl}</div>
    </article>
  </div>

  <section class='feedback-card' style='padding:1rem;' aria-label='All detected notes'>
    <div style='font-size:var(--text-sm);font-weight:700;color:var(--color-text);margin-bottom:0.75rem;'>Detected notes</div>
    <div>{chips_html}</div>
  </section>
</section>
"""


def render_feedback_html(fb: dict, instrument: str, age_group: str):
    grade_col = _color("green") if fb["accuracy"] >= 80 else (
                _color("gold") if fb["accuracy"] >= 65 else _color("red"))
    cons_col  = _color("green") if fb["consistency"] >= 75 else (
                _color("gold") if fb["consistency"] >= 55 else _color("red"))

    tips_html = ""
    for tip in fb["tips"]:
        col = _color(tip["color"])
        tips_html += (
            f"<li style='display:flex;gap:0.75rem;align-items:flex-start;padding:0.9rem 0;border-top:1px solid var(--color-divider);'>"
            f"<span aria-hidden='true' style='display:inline-flex;align-items:center;justify-content:center;min-width:2rem;height:2rem;border-radius:999px;background:color-mix(in srgb, {col} 14%, var(--color-surface));color:{col};font-weight:800;'>{tip['icon']}</span>"
            f"<span style='color:var(--color-text);font-size:var(--text-base);line-height:1.65;'>{tip['text']}</span></li>"
        )

    emoji = {"Guitar": "🎸", "Piano": "🎹", "Voice": "🎤", "Clarinet": "🎼"}.get(instrument,"🎵")

    return f"""
<section class='feedback-card' style='padding:1.5rem;' aria-labelledby='feedback-title'>
  <div class='sec-label' style='margin-top:0 !important;'>Performance feedback</div>
  <h2 id='feedback-title' class='sec-title' style='margin-bottom:0.75rem !important;'>Practice notes for {instrument}</h2>
  <p style='margin:0 0 1rem;color:var(--color-text-muted);font-size:var(--text-base);'>{emoji} Tailored for {age_group}</p>

  <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.9rem;margin-bottom:1rem;'>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:clamp(1.8rem,4vw,2.4rem);font-weight:800;color:{grade_col};line-height:1;'>{fb['accuracy']:.0f}%</div>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-top:0.45rem;'>Pitch accuracy</div>
    </article>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:clamp(1.6rem,4vw,2.2rem);font-weight:800;color:{_color("blue")};line-height:1;'>{fb['grade']}</div>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-top:0.45rem;'>Intonation grade</div>
    </article>
    <article class='stat-card' style='padding:1rem;text-align:center;'>
      <div style='font-size:clamp(1.1rem,2.6vw,1.45rem);font-weight:800;color:{cons_col};line-height:1.2;'>{fb['cons_label']}</div>
      <div style='font-size:var(--text-sm);font-weight:600;color:var(--color-text-muted);margin-top:0.45rem;'>Consistency</div>
    </article>
  </div>

  <section style='padding:1rem 1.1rem;border-radius:var(--radius-lg);background:color-mix(in srgb, var(--color-primary) 5%, var(--color-surface));border:1px solid var(--color-border);margin-bottom:1rem;' aria-label='Performance overview'>
    <p style='margin:0;color:var(--color-text);font-size:var(--text-base);line-height:1.75;'>{fb['overview']}</p>
  </section>

  <section aria-label='Practice tips'>
    <div style='font-size:var(--text-sm);font-weight:700;color:var(--color-text);margin-bottom:0.25rem;'>Suggested next steps</div>
    <ul style='list-style:none;padding:0;margin:0;'>{tips_html}</ul>
  </section>
</section>
"""


# ── Main analysis function ───────────────────────────────────────────────────

def analyze(audio_path, instrument, age_group):
    """Called by Gradio on every Submit click."""
    
    if audio_path is None:
        empty = "<div style='background:#141417;border:1px solid #2a2a32;padding:40px;" \
                "text-align:center;color:#6b6b7a;font-family:JetBrains Mono,monospace;" \
                "font-size:11px;letter-spacing:2px;'>No audio provided.</div>"
        return empty, empty

    freq, note, cents, accuracy, consistency, all_notes, error = \
        detect_pitch_and_note(audio_path, instrument)

    if error or note is None:
        msg = error or "No clear pitch detected. Play a single sustained note clearly."
        err_html = (
            f"<div style='background:#141417;border:1px solid #d9534f;padding:20px;"
            f"font-family:JetBrains Mono,monospace;font-size:12px;color:#d9534f;"
            f"letter-spacing:1px;'>{msg}</div>"
        )
        return err_html, err_html

    pitch_html  = render_pitch_html(note, freq, cents, accuracy, consistency, all_notes)
    fb_dict     = generate_feedback(instrument, note, freq, cents,
                                    accuracy, consistency, age_group, all_notes)
    fb_html     = render_feedback_html(fb_dict, instrument, age_group)

    return pitch_html, fb_html


# ── Gradio UI ────────────────────────────────────────────────────────────────

def build_demo():
    with gr.Blocks(css=CSS, title="Audiophile — Pitch Detection") as demo:

        # Header
        gr.HTML("""
        <div id="audiophile-header">
            <h1>Audio<span>phile</span></h1>
            <p>Record | Detect | Improve</p>
            <p>Upload your audio file. Become an Audiophile.</p>
        </div>
        """)

        # ── First tab - Input ──────────────────────────────────────
        with gr.Tab("Instruments and Audio"):
            # left column
            with gr.Column(scale=1):

                gr.HTML("""
                <aside>
                    <div class="eyebrow" id="secondary">Instructions</div>
                    <h2 id="left" class="serif" style="margin-top: 0.75rem">For your submission</h2>
                    <hr class="rule" />
                    <ol class="steps">
                        <li class="step">
                            <div class="step-num">1</div>
                            <div>
                                <div class="step-title">Select your instrument and age group</div>
                            </div>
                        </li>
                        <li class="step">
                            <div class="step-num">2</div>
                            <div>
                                <div class="step-title">Click the mic to record, or upload an audio file</div>
                            </div>
                        </li>
                        <li class="step">
                            <div class="step-num">3</div>
                            <div>
                                <div class="step-title">Play a note or short phrase (2–5 seconds works well)</div>
                            </div>
                        </li>
                        <li class="step">
                            <div class="step-num">4</div>
                            <div>
                                <div class="step-title">Click 'Analyze' to run pitch detection</div>
                            </div>
                        </li>
                        <li class="step">
                            <div class="step-num">5</div>
                            <div>
                                <div class="step-title">Click 'Feedback' in top right to review</div>
                            </div>
                        </li>
                    </ol>

                    <div class="paper note">
                        <div class="eyebrow">A note on privacy</div>
                        <p>Your recording is held in the browser only — it never leaves this page. Refresh the tab and it is gone.</p>
                    </div>
                </aside>
                """)

            gr.HTML("<div class='sec-label' style='padding:0 0 2px;'>Step 01</div>"
                    "<div class='sec-title' style='padding:0 0 12px;'>Configure</div>")

            with gr.Column(scale=1):
                instrument = gr.Dropdown(
                    choices=INSTRUMENTS,
                    value="Guitar",
                    label="Instrument",
                    interactive=True,
                    show_label=True,    
                )

                age_group = gr.Dropdown(
                    choices=AGE_GROUPS,
                    value="Adult (18+)",
                    label="Age Group",
                    interactive=True,
                )

                gr.HTML("""
                    <section>
                        <form id="submission-form" class="frame form" novalidate>
                            <div class="form-head">
                                <div>
                                    <div class="eyebrow">Recording and Submission</div>
                                    <h2 class="serif" id="left">Your recording</h2>
                                </div>
                                <span class="formats">mp3 · wav · m4a</span>
                            </div>

                            <hr class="rule" />

                            <label id="dropzone" class="dropzone" for="file-input">
                                <input id="file-input" type="file" accept="audio/*" />
                                <div id="dz-empty">
                                    <div class="dropzone-title">Place your recording here.</div>
                                    <p class="dropzone-hint">Drag a file in, or <span class="gold-underline">browse your library</span>.</p>
                                    <p class="dropzone-cap">up to 25 MB</p>
                                </div>
                                <div id="dz-filled" class="hidden">
                                    <div class="file-name" id="file-name"></div>
                                    <div class="file-meta" id="file-meta"></div>
                                    <button type="button" id="remove-file" class="remove-btn">Remove</button>
                                </div>
                            </label>

                            <div class="fields">
                                <label class="field">
                                    <span class="eyebrow field-label">Instrument</span>
                                    <select id="instr">
                                        <option>Guitar</option>
                                        <option>Piano</option>
                                        <option>Voice</option>
                                        <option>Clarinet</option>
                                    </select>
                                </label>
                                <label class="field">
                                    <span class="eyebrow field-label">Age Group</span>
                                    <select id="ages">
                                        <option>Child (6-12)</option>
                                        <option>Teen (13-18)</option>
                                        <option>Adult (18+)</option>
                                    </select>
                                </label>
                            </div>

                            <div class="actions">
                                <button id="submit-btn" type="submit" class="btn-primary">
                                    <span id="submit-label">Analyze</span>
                                    <span aria-hidden="true">→</span>
                                </button>
                            </div>
                        </form>
                    </section>
                """)

                # gr.HTML("<div class='sec-label' style='margin-top:24px;padding:0 0 2px;'>Step 02</div>"
                #         "<div class='sec-title' style='padding:0 0 12px;'>Record or Upload</div>")

                audio_input = gr.Audio(
                    sources=["microphone", "upload"],
                    type="filepath",
                    label="🎙️  Record or upload .wav / .mp3",
                    format="wav",
                )

                analyze_btn = gr.Button("⚡  Analyze Performance", variant="primary")

        # ── Second tab - Feedback ────────────────────────────────────
        with gr.Tab("Pitches and Feedback"):

            gr.HTML("<div class='sec-label' style='margin-top:16px;padding:0 0 2px;'>Step 03</div>"
                    "<div class='sec-title' style='padding:0 0 12px;'>Pitch Detection</div>")

            pitch_out = gr.HTML(
                value="<div style='background:#141417;border:1px solid #2a2a32;padding:40px;"
                        "text-align:center;color:#6b6b7a;font-family:\"JetBrains Mono\",monospace;"
                        "font-size:11px;letter-spacing:2px;'>"
                        "Record or upload audio, then click Analyze.</div>"
            )

            gr.HTML("<div class='sec-label' style='margin-top:24px;padding:0 0 2px;'>Step 04</div>"
                    "<div class='sec-title' style='padding:0 0 12px;'>Feedback</div>")

            feedback_out = gr.HTML(
                value="<div style='background:#141417;border:1px solid #2a2a32;padding:40px;"
                        "text-align:center;color:#6b6b7a;font-family:\"JetBrains Mono\",monospace;"
                        "font-size:11px;letter-spacing:2px;'>"
                        "Feedback will appear here after analysis.</div>"
            )

        # ── Wire up ──────────────────────────────────────────────────────
        analyze_btn.click(
            fn=analyze,
            inputs=[audio_input, instrument, age_group],
            outputs=[pitch_out, feedback_out],
        )

    return demo


if __name__ == "__main__":
    app = build_demo()
    app.launch()