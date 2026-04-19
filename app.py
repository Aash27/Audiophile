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
# with open("styles.css", "r") as f:
#     CSS = f.read()

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

    with gr.Blocks(title="Audiophile — Pitch Detection") as demo:

        # Hero
        gr.HTML("""
            <section class="container hero center">
                <h1 style="margin-top: 1.5rem; font-size: 5vw">
                    <span class="sans">Audiophile</span>,<br />
                    <em id="comma">for the love of Music</em>
                </h1>
                <p>Submit or record a single recording and receive feedback.</p>
            </section>
        """)

        with gr.Tabs():

            # ── First tab - Input ──────────────────────────────────────
            with gr.Tab("Instruments and Audio", elem_classes="recital-tabs"):

                with gr.Row():

                    with gr.Column(scale=2):

                        gr.HTML("""
                            <div class="container layout">
                                <!-- Instructions -->
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

                    with gr.Column(scale=1):

                        with gr.Row():

                            instrument = gr.Dropdown(
                                choices=INSTRUMENTS,
                                value="Guitar",
                                label="Instrument",
                                interactive=True,
                                elem_classes="recital-dropdown"
                            )

                            age_group = gr.Dropdown(
                                choices=AGE_GROUPS,
                                value="Adult (18+)",
                                label="Age Group",
                                interactive=True,
                                elem_classes="recital-dropdown"
                            )

                        audio_input = gr.Audio(
                            sources=["microphone", "upload"],
                            type="filepath",
                            label="🎙️  Record or upload .wav / .mp3",
                            format="wav",
                            elem_classes="recital-dropdowns"
                        )

                        analyze_btn = gr.Button("⚡  Analyze Performance", variant="primary")

            # ── Second tab - Feedback ────────────────────────────────────
            with gr.Tab("Pitches and Feedback", elem_classes="recital-tabs"):

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
    app.launch(css_paths="styles.css")