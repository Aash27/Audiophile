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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Global ── */
*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container, #root {
    background: #0d0d0f !important;
    color: #f0ede6 !important;
    font-family: 'Lato', sans-serif !important;
}

footer { display: none !important; }

/* ── Header ── */
#audiophile-header {
    background:
        linear-gradient(rgba(10,7,4,0.80), rgba(10,7,4,0.80)),
        url('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1400&q=80')
        center / cover no-repeat;
    padding: 52px 40px 44px;
    text-align: center;
    border-bottom: 1px solid #2a2a32;
    margin-bottom: 0;
}
#audiophile-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: clamp(28px, 4vw, 52px);
    font-weight: 400;
    color: #f0ede6;
    margin: 0 0 8px;
}
#audiophile-header h1 span { font-style: italic; color: #c8a96e; }
#audiophile-header p {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: #a89880;
    font-size: 17px;
    margin: 0;
}

/* ── Section labels ── */
.sec-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #6b6b7a !important;
    margin-bottom: 6px !important;
}
.sec-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 20px !important;
    color: #f0ede6 !important;
    margin-bottom: 4px !important;
}

/* ── Gradio panels / boxes ── */
.gr-panel, .gr-box, .gr-form, .panel,
div[data-testid="column"],
.block, .prose {
    background: #141417 !important;
    border-color: #2a2a32 !important;
    border-radius: 0 !important;
}

/* ── Labels ── */
label, .label-wrap span, .svelte-1gfkn6j {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #a89880 !important;
}

/* ── Inputs / dropdowns ── */
input, select, textarea,
.gr-dropdown select,
.wrap select {
    background: #1c1c21 !important;
    border: 1px solid #2a2a32 !important;
    border-radius: 0 !important;
    color: #1c1c21 !important;
    font-family: 'Lato', sans-serif !important;
    font-size: 14px !important;
}
input:focus, select:focus { border-color: #c8a96e !important; outline: none !important; }

/* ── Buttons ── */
button.primary, .primary {
    background: #c8a96e !important;
    color: #0d0d0f !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    transition: box-shadow .2s !important;
}
button.primary:hover { box-shadow: 0 0 20px rgba(200,169,110,.35) !important; }

button.secondary {
    background: transparent !important;
    color: #f0ede6 !important;
    border: 1px solid #2a2a32 !important;
    border-radius: 0 !important;
    font-family: 'Lato', sans-serif !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
}
button.secondary:hover { border-color: #a89880 !important; }

/* ── Audio recorder ── */
.audio-recorder, [data-testid="audio"] {
    background: #1c1c21 !important;
    border: 1px solid #2a2a32 !important;
    border-radius: 0 !important;
}

/* ── Output HTML ── */
.output-html, [data-testid="html"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Tabs ── */
.tab-nav {
    background: #141417 !important;
    border-bottom: 1px solid #2a2a32 !important;
}
.tab-nav button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #6b6b7a !important;
    border-radius: 0 !important;
    background: transparent !important;
}
.tab-nav button.selected {
    color: #c8a96e !important;
    border-bottom: 2px solid #c8a96e !important;
}

/* ── Markdown / prose ── */
.prose p, .prose li { color: #d0cdc5 !important; font-size: 14px !important; line-height: 1.7 !important; }
.prose strong { color: #c8a96e !important; }
.prose h3 { font-family: 'Playfair Display', serif !important; color: #f0ede6 !important; }
"""


# ── HTML builders ────────────────────────────────────────────────────────────

def _color(key):
    return {
        "green": "#4ecb8d",
        "red":   "#d9534f",
        "blue":  "#5b9bd5",
        "gold":  "#c8a96e",
        "muted": "#6b6b7a",
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
            pct = cnt / total * 100
            chips_html += (
                f"<span style='border:1px solid #2a2a32;color:#a89880;"
                f"padding:3px 12px;font-family:JetBrains Mono,monospace;"
                f"font-size:11px;letter-spacing:1px;margin:2px;display:inline-block;'>"
                f"{n} <span style='opacity:.5;font-size:9px'>{pct:.0f}%</span></span>"
            )

    return f"""
<div style='font-family:Lato,sans-serif;background:#141417;border:1px solid #2a2a32;padding:28px;color:#f0ede6;'>

  <div style='font-family:"JetBrains Mono",monospace;font-size:9px;letter-spacing:3px;
              text-transform:uppercase;color:#6b6b7a;margin-bottom:18px;'>
    Pitch Analysis Results
  </div>

  <!-- Stat cards -->
  <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;'>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;margin-bottom:8px;font-family:"JetBrains Mono",monospace;'>Dominant Note</div>
      <div style='font-size:32px;font-weight:700;color:{tune_col};font-family:"JetBrains Mono",monospace;'>{note}</div>
      <div style='font-size:10px;color:#6b6b7a;margin-top:4px;font-family:"JetBrains Mono",monospace;'>Letter Notation</div>
    </div>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;margin-bottom:8px;font-family:"JetBrains Mono",monospace;'>Frequency</div>
      <div style='font-size:28px;font-weight:700;color:#f0ede6;font-family:"JetBrains Mono",monospace;'>{frequency:.1f}</div>
      <div style='font-size:10px;color:#6b6b7a;margin-top:4px;font-family:"JetBrains Mono",monospace;'>Hz</div>
    </div>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;margin-bottom:8px;font-family:"JetBrains Mono",monospace;'>Intonation</div>
      <div style='font-size:18px;font-weight:700;color:{tune_col};font-family:"JetBrains Mono",monospace;'>{tune_str}</div>
    </div>
  </div>

  <!-- Tuner meter -->
  <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;margin-bottom:20px;'>
    <div style='display:flex;justify-content:space-between;font-family:"JetBrains Mono",monospace;
                font-size:9px;letter-spacing:2px;color:#6b6b7a;margin-bottom:12px;'>
      <span>♭ Flat</span><span>● In Tune</span><span>Sharp ♯</span>
    </div>
    <div style='position:relative;height:10px;background:#2a2a32;border-radius:5px;'>
      <div style='position:absolute;top:-4px;bottom:-4px;left:50%;width:2px;
                  background:rgba(255,255,255,.2);transform:translateX(-50%);'></div>
      <div style='position:absolute;top:-6px;left:{needle_pct:.0f}%;width:4px;height:22px;
                  background:{tune_col};border-radius:2px;transform:translateX(-50%);
                  box-shadow:0 0 8px {tune_col};'></div>
    </div>
  </div>

  <!-- Score row -->
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;'>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:14px;display:flex;
                align-items:center;justify-content:space-between;'>
      <span style='font-family:"JetBrains Mono",monospace;font-size:9px;letter-spacing:2px;
                   text-transform:uppercase;color:#6b6b7a;'>Pitch Accuracy</span>
      <span style='font-family:"JetBrains Mono",monospace;font-size:22px;font-weight:700;
                   color:{grade_col};'>{accuracy:.0f}%</span>
    </div>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:14px;display:flex;
                align-items:center;justify-content:space-between;'>
      <span style='font-family:"JetBrains Mono",monospace;font-size:9px;letter-spacing:2px;
                   text-transform:uppercase;color:#6b6b7a;'>Consistency</span>
      <span style='font-family:"JetBrains Mono",monospace;font-size:22px;font-weight:700;
                   color:{cons_col};'>{cons_lbl}</span>
    </div>
  </div>

  <!-- All notes -->
  <div style='font-family:"JetBrains Mono",monospace;font-size:9px;letter-spacing:2px;
              text-transform:uppercase;color:#6b6b7a;margin-bottom:8px;'>
    All Notes Detected
  </div>
  <div style='margin-bottom:4px;'>{chips_html}</div>

</div>
"""


def render_feedback_html(fb: dict, instrument: str, age_group: str):
    """Build the styled feedback panel."""
    grade_col = _color("green") if fb["accuracy"] >= 80 else (
                _color("gold") if fb["accuracy"] >= 65 else _color("red"))
    cons_col  = _color("green") if fb["consistency"] >= 75 else (
                _color("gold") if fb["consistency"] >= 55 else _color("red"))

    tips_html = ""
    for tip in fb["tips"]:
        col = _color(tip["color"])
        tips_html += (
            f"<div style='display:flex;gap:12px;font-size:13px;line-height:1.6;"
            f"color:#b0ab9f;margin-bottom:10px;align-items:flex-start;'>"
            f"<span style='color:{col};font-weight:700;flex-shrink:0;margin-top:1px;'>"
            f"{tip['icon']}</span>"
            f"<span>{tip['text']}</span></div>"
        )

    emoji = {"Guitar": "🎸", "Piano": "🎹", "Voice": "🎤", "Clarinet": "🎼"}.get(instrument,"🎵")

    return f"""
<div style='font-family:Lato,sans-serif;background:#141417;border:1px solid #2a2a32;padding:28px;color:#f0ede6;'>

  <div style='font-family:"JetBrains Mono",monospace;font-size:9px;letter-spacing:3px;
              text-transform:uppercase;color:#6b6b7a;margin-bottom:18px;'>
    Performance Feedback · {emoji} {instrument} · {age_group}
  </div>

  <!-- Score cards -->
  <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;'>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:34px;font-weight:700;color:{grade_col};
                  font-family:"JetBrains Mono",monospace;'>{fb["accuracy"]:.0f}%</div>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;
                  margin-top:4px;font-family:"JetBrains Mono",monospace;'>Pitch Accuracy</div>
    </div>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:34px;font-weight:700;color:{_color("blue")};
                  font-family:"JetBrains Mono",monospace;'>{fb["grade"]}</div>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;
                  margin-top:4px;font-family:"JetBrains Mono",monospace;'>Intonation Grade</div>
    </div>
    <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;text-align:center;'>
      <div style='font-size:26px;font-weight:700;color:{cons_col};
                  font-family:"JetBrains Mono",monospace;'>{fb["cons_label"]}</div>
      <div style='font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;
                  margin-top:4px;font-family:"JetBrains Mono",monospace;'>Consistency</div>
    </div>
  </div>

  <!-- Overview block -->
  <div style='background:#1c1c21;border:1px solid #2a2a32;border-left:3px solid #c8a96e;
              padding:20px;margin-bottom:20px;'>
    <p style='font-size:14px;line-height:1.8;color:#ccc9c0;margin:0;'>{fb["overview"]}</p>
  </div>

  <!-- Tips -->
  {tips_html}

</div>
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
          <p>Record. Detect. Improve.</p>
        </div>
        """)

        # ── Left column: inputs ──────────────────────────────────────
        with gr.Tab("Instruments and Audio"):

            gr.HTML("""
            <div style='background:#1c1c21;border:1px solid #2a2a32;padding:16px;
                        margin-top:16px;margin-bottom:20px;'>
                <div style='font-family:"JetBrains Mono",monospace;font-size:9px;
                            letter-spacing:2px;text-transform:uppercase;color:#6b6b7a;
                            margin-bottom:10px;'>How to use</div>
                <div style='font-size:13px;color:#a89880;line-height:1.8;'>
                ① Select your instrument and age group<br>
                ② Click the mic to record, or upload an audio file<br>
                ③ Play a note or short phrase (2–5 seconds works well)<br>
                ④ Click <strong style='color:#c8a96e;'>Analyze</strong> to run pitch detection<br>
                ⑤ Review pitch data and your personalized feedback
                </div>
            </div>
            """)

            gr.HTML("<div class='sec-label' style='padding:0 0 2px;'>Step 01</div>"
                    "<div class='sec-title' style='padding:0 0 12px;'>Configure</div>")

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

            gr.HTML("<div class='sec-label' style='margin-top:24px;padding:0 0 2px;'>Step 02</div>"
                    "<div class='sec-title' style='padding:0 0 12px;'>Record or Upload</div>")

            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="🎙️  Record or upload .wav / .mp3",
                format="wav",
            )

            analyze_btn = gr.Button("⚡  Analyze Performance", variant="primary")

        # ── Right column: outputs ────────────────────────────────────
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