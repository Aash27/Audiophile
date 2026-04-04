"""
feedback.py
Generates instrument-specific, age-adjusted performance feedback using Groq API.

Tone rules:
  Child  (6-12)  — warm, encouraging, simple language, fun metaphors
  Teen   (13-18) — honest, specific, direct, no fluff
  Adult  (18+)   — technical, precise, professional, zero hand-holding

Groq is used to generate the detailed overview and per-pitch analysis.
All structured data (grade, tips, consistency) is still computed locally
so the UI never hangs if Groq is unavailable.
"""

import os
import json
import time
import requests

from instruments import INSTRUMENT_TIPS

# ── Groq config ──────────────────────────────────────────────────────────────
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL  = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama3-70b-8192"          # fast + high quality
GROQ_TIMEOUT  = 15                          # seconds


# ── Local helpers ────────────────────────────────────────────────────────────

def grade_from_accuracy(accuracy: float) -> str:
    if accuracy >= 90: return "A"
    if accuracy >= 82: return "B+"
    if accuracy >= 74: return "B"
    if accuracy >= 65: return "C+"
    if accuracy >= 55: return "C"
    return "D"


def consistency_label(consistency: float) -> str:
    if consistency >= 85: return "Solid"
    if consistency >= 70: return "Fair"
    if consistency >= 55: return "Unstable"
    return "Erratic"


def intonation_label(cents: float) -> tuple:
    """Return (label, direction) e.g. ('Sharp ♯', 'sharp')"""
    if abs(cents) <= 10:
        return "In Tune ✓", "intune"
    elif cents > 0:
        return f"+{cents:.0f}¢  Sharp ♯", "sharp"
    else:
        return f"{cents:.0f}¢  Flat ♭", "flat"


def _direction(cents: float) -> str:
    if abs(cents) <= 10:
        return "intune"
    return "sharp" if cents > 0 else "flat"


# ── Groq call ────────────────────────────────────────────────────────────────

def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """
    Call Groq chat completions. Returns the assistant text or raises.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.55,
        "max_tokens": 1400,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }
    resp = requests.post(GROQ_API_URL, headers=headers,
                         json=payload, timeout=GROQ_TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── System prompts per age group ─────────────────────────────────────────────

_SYSTEM = {
    "Child (6-12)": (
        "You are a kind, encouraging music teacher for young children aged 6-12. "
        "Use simple, friendly language. Avoid jargon. Use short sentences and "
        "fun analogies (animals, games, colours). Always end on a positive note. "
        "Never sound harsh or clinical. Format your response ONLY as valid JSON — "
        "no markdown, no preamble, no explanation outside the JSON object."
    ),
    "Teen (13-18)": (
        "You are a direct, no-nonsense music coach for teenagers aged 13-18. "
        "Be honest and specific. Skip the fluff. Use music terminology correctly "
        "but explain it briefly. Don't patronise. Be encouraging through precision, "
        "not through empty praise. Format your response ONLY as valid JSON — "
        "no markdown, no preamble, no explanation outside the JSON object."
    ),
    "Adult (18+)": (
        "You are a professional music performance coach for adult musicians. "
        "Be technical, precise, and concise. Assume the musician understands "
        "standard music terminology: cents, Hz, intonation, embouchure, vibrato, "
        "support, etc. Do not over-explain. Focus on actionable diagnosis and "
        "correction. Format your response ONLY as valid JSON — "
        "no markdown, no preamble, no explanation outside the JSON object."
    ),
}


# ── Build user prompt ────────────────────────────────────────────────────────

def _build_user_prompt(
    instrument: str,
    note: str,
    frequency: float,
    cents: float,
    accuracy: float,
    consistency: float,
    age_group: str,
    all_notes: list,
    pitch_timeline: list,          # list of {time_s, note, cents, hz}
) -> str:
    """
    Construct the detailed prompt sent to Groq.
    pitch_timeline is a list of dicts — each frame/window from the detector.
    """

    direction  = _direction(cents)
    grade      = grade_from_accuracy(accuracy)
    cons_lbl   = consistency_label(consistency)
    tune_label, _ = intonation_label(cents)

    # Summarise the timeline into a readable table (max 30 rows to keep prompt tight)
    if pitch_timeline:
        timeline_rows = pitch_timeline[:30]
        timeline_str  = "\n".join(
            f"  t={r['time_s']:.2f}s  note={r['note']}  "
            f"hz={r['hz']:.1f}  cents={r['cents']:+.0f}¢  "
            f"status={'IN TUNE' if abs(r['cents']) <= 10 else ('SHARP' if r['cents'] > 0 else 'FLAT')}"
            for r in timeline_rows
        )
        if len(pitch_timeline) > 30:
            timeline_str += f"\n  ... ({len(pitch_timeline) - 30} more frames)"
    else:
        timeline_str = "  (no timeline data available)"

    # Summarise all_notes
    if all_notes:
        total = sum(c for _, c in all_notes)
        notes_summary = ", ".join(
            f"{n} ({cnt/total*100:.0f}%)" for n, cnt in all_notes
        )
    else:
        notes_summary = note

    prompt = f"""
Instrument    : {instrument}
Age group     : {age_group}
Dominant note : {note}  ({frequency:.1f} Hz)
Intonation    : {tune_label}  ({cents:+.1f}¢)
Pitch accuracy: {accuracy:.1f}%  (Grade: {grade})
Consistency   : {cons_lbl}  ({consistency:.0f}/100)
All notes seen: {notes_summary}

PITCH TIMELINE (every detected pitch window):
{timeline_str}

---
Respond with a single JSON object with EXACTLY these keys:

{{
  "overview": "<2-4 sentence paragraph — age-appropriate overall assessment>",
  "timeline_analysis": [
    {{
      "time_range": "<e.g. 0.00s – 0.50s>",
      "note": "<note name>",
      "issue": "<'in_tune' | 'sharp' | 'flat' | 'unstable'>",
      "cents_deviation": <float>,
      "comment": "<specific, age-appropriate 1-sentence diagnosis for THIS moment>"
    }}
    // one entry per distinct pitch event or problem cluster — max 8 entries
  ],
  "primary_issue": "<single sentence — the #1 thing to fix>",
  "correction_drill": "<age-appropriate specific practice drill — 2-3 sentences>",
  "encouragement": "<1 closing sentence — age-appropriate tone>"
}}

Rules:
- timeline_analysis must group nearby frames into meaningful events (don't list every frame).
- comment in each timeline entry must reference the exact time and what went wrong.
- All text must match the tone for {age_group}.
- Return ONLY the JSON. No markdown fences, no extra text.
"""
    return prompt.strip()


# ── Fallback (no Groq / API error) ───────────────────────────────────────────

def _local_fallback(
    instrument: str,
    note: str,
    frequency: float,
    cents: float,
    accuracy: float,
    consistency: float,
    age_group: str,
    all_notes: list,
) -> dict:
    """
    Pure-Python fallback used when Groq is unavailable.
    Returns the same schema as the Groq path.
    """
    direction = _direction(cents)
    grade     = grade_from_accuracy(accuracy)
    cons_lbl  = consistency_label(consistency)
    tune_label, _ = intonation_label(cents)

    tips_bank    = INSTRUMENT_TIPS.get(instrument, INSTRUMENT_TIPS["Guitar"])
    key          = direction if direction != "intune" else "general"
    tip1, tip2   = tips_bank[key][0], tips_bank[key][1]
    general_tip  = tips_bank["general"][0]

    if age_group == "Child (6-12)":
        if direction == "intune":
            overview = (
                f"You hit {note} right in the center — great job! "
                f"Your pitch accuracy is {accuracy:.0f}%. "
                f"Keep practising and your consistency will grow too."
            )
        elif direction == "sharp":
            overview = (
                f"Your note {note} is a little too high — {abs(cents):.0f} cents sharp. "
                f"Think of it like a balloon that floated too far up — we just need to "
                f"bring it back down a tiny bit. You can fix this!"
            )
        else:
            overview = (
                f"Your note {note} is landing a little too low — {abs(cents):.0f} cents flat. "
                f"It's like a ball that didn't quite reach the basket. "
                f"A small adjustment and you'll nail it."
            )
    elif age_group == "Teen (13-18)":
        if direction == "intune":
            overview = (
                f"{note} centered at {frequency:.1f} Hz — {abs(cents):.0f}¢ deviation. "
                f"Pitch accuracy: {accuracy:.0f}%. "
                f"{'Consistency is strong too.' if consistency >= 75 else 'Work on sustaining that accuracy — consistency is still shaky.'}"
            )
        elif direction == "sharp":
            overview = (
                f"{note} is {abs(cents):.0f}¢ sharp — audible in any ensemble. "
                f"Accuracy: {accuracy:.0f}%. "
                f"It's a consistent habit, which means it's fixable with the right drill."
            )
        else:
            overview = (
                f"{note} is {abs(cents):.0f}¢ flat. Accuracy: {accuracy:.0f}%. "
                f"A flat tendency is one adjustable variable — easier to fix than random drift."
            )
    else:
        if direction == "intune":
            overview = (
                f"Dominant pitch {note} at {frequency:.1f} Hz — deviation {abs(cents):.1f}¢. "
                f"Accuracy: {accuracy:.0f}% | Consistency: {cons_lbl} ({consistency:.0f}/100). "
                f"{'Clean session. Maintain under faster tempos and higher dynamics.' if accuracy >= 80 else 'Intonation centre is good; frame-to-frame consistency is the limiting factor. Long tones.'}"
            )
        elif direction == "sharp":
            overview = (
                f"{note} at {frequency:.1f} Hz running {abs(cents):.1f}¢ sharp. "
                f"Accuracy: {accuracy:.0f}% | Consistency: {cons_lbl}. "
                f"Consistent sharpness is a reproducible error — easier to correct than random drift."
            )
        else:
            overview = (
                f"{note} at {frequency:.1f} Hz sitting {abs(cents):.1f}¢ flat. "
                f"Accuracy: {accuracy:.0f}% | Consistency: {cons_lbl}. "
                f"Single-variable problem. Isolate the cause and the rest of your intonation follows."
            )

    primary_issue = tip1
    correction_drill = tip2
    encouragement = (
        "Keep going — every minute of focused practice compounds." if age_group == "Adult (18+)"
        else "You're improving — keep at it!" if age_group == "Teen (13-18)"
        else "Great effort — keep playing and you'll keep getting better! 🎵"
    )

    return {
        "overview":          overview,
        "timeline_analysis": [],
        "primary_issue":     primary_issue,
        "correction_drill":  correction_drill,
        "encouragement":     encouragement,
        "grade":             grade_from_accuracy(accuracy),
        "accuracy":          accuracy,
        "consistency":       consistency,
        "cons_label":        cons_lbl,
        "tune_label":        tune_label,
        "direction":         direction,
        # Legacy tips list for render_feedback_html compatibility
        "tips": _build_tips(instrument, note, cents, accuracy, consistency, age_group, direction, tip1, tip2, general_tip),
    }


def _build_tips(instrument, note, cents, accuracy, consistency, age_group,
                direction, tip1, tip2, general_tip):
    cons_lbl = consistency_label(consistency)
    tips = []

    if direction == "intune":
        tips.append({
            "icon": "✓", "color": "green",
            "text": f"Pitch centre is solid — {note} within {abs(cents):.0f}¢ of perfect. "
                    f"Maintain this under pressure."
        })
    elif direction == "sharp":
        tips.append({
            "icon": "↑", "color": "red",
            "text": f"{note} is {abs(cents):.0f}¢ sharp. This is your primary target."
        })
    else:
        tips.append({
            "icon": "↓", "color": "blue",
            "text": f"{note} is {abs(cents):.0f}¢ flat. Address this before anything else."
        })

    tips.append({"icon": "→", "color": "gold", "text": tip1})
    tips.append({"icon": "→", "color": "gold", "text": tip2})

    if consistency >= 75:
        tips.append({
            "icon": "✓", "color": "green",
            "text": f"Pitch consistency: {cons_lbl} ({consistency:.0f}/100). Controlled playing."
        })
    else:
        tips.append({
            "icon": "△", "color": "muted",
            "text": f"Consistency: {cons_lbl} ({consistency:.0f}/100). "
                    f"Pitch is drifting between notes. Long tones with a drone will fix this fastest."
        })

    if age_group == "Child (6-12)":
        tips.append({
            "icon": "■", "color": "muted",
            "text": f"Practice: play {note} as a long slow note and count to 4 while holding it. "
                    f"Try to keep the sound steady the whole time."
        })
    elif age_group == "Teen (13-18)":
        tips.append({
            "icon": "■", "color": "muted",
            "text": f"Drill: record {note} sustained for 4 beats at 60 bpm. "
                    f"Check tuner at start vs end. If it drifts, that's a support issue."
        })
    else:
        tips.append({"icon": "■", "color": "muted", "text": general_tip})

    return tips


# ── Groq response parser ──────────────────────────────────────────────────────

def _parse_groq_response(raw: str, accuracy: float, consistency: float,
                         cents: float, instrument: str, note: str,
                         age_group: str) -> dict:
    """
    Parse Groq JSON, attach computed fields, build legacy tips list.
    Falls back gracefully on any parse error.
    """
    # Strip accidental markdown fences
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()

    data = json.loads(text)          # may raise — caught upstream

    direction  = _direction(cents)
    grade      = grade_from_accuracy(accuracy)
    cons_lbl   = consistency_label(consistency)
    tune_label, _ = intonation_label(cents)

    tips_bank   = INSTRUMENT_TIPS.get(instrument, INSTRUMENT_TIPS["Guitar"])
    key         = direction if direction != "intune" else "general"
    tip1, tip2  = tips_bank[key][0], tips_bank[key][1]
    general_tip = tips_bank["general"][0]

    tips = _build_tips(instrument, note, cents, accuracy, consistency,
                       age_group, direction, tip1, tip2, general_tip)

    # Inject Groq-generated primary issue and drill as extra tips
    if data.get("primary_issue"):
        tips.append({
            "icon": "⚑", "color": "red",
            "text": data["primary_issue"]
        })
    if data.get("correction_drill"):
        tips.append({
            "icon": "◈", "color": "gold",
            "text": data["correction_drill"]
        })
    if data.get("encouragement"):
        tips.append({
            "icon": "★", "color": "green",
            "text": data["encouragement"]
        })

    return {
        "overview":          data.get("overview", ""),
        "timeline_analysis": data.get("timeline_analysis", []),
        "primary_issue":     data.get("primary_issue", ""),
        "correction_drill":  data.get("correction_drill", ""),
        "encouragement":     data.get("encouragement", ""),
        "grade":             grade,
        "accuracy":          accuracy,
        "consistency":       consistency,
        "cons_label":        cons_lbl,
        "tune_label":        tune_label,
        "direction":         direction,
        "tips":              tips,
    }


# ── Public API ────────────────────────────────────────────────────────────────

def generate_feedback(
    instrument: str,
    note: str,
    frequency: float,
    cents: float,
    accuracy: float,
    consistency: float,
    age_group: str,
    all_notes: list,
    pitch_timeline: list = None,   # optional: list of {time_s, note, hz, cents}
) -> dict:
    """
    Main entry point. Returns feedback dict compatible with render_feedback_html.

    Attempts Groq first; falls back to local generation on any failure.

    pitch_timeline format (each element):
        {
            "time_s": float,   # seconds from start
            "note":   str,     # e.g. "A4"
            "hz":     float,
            "cents":  float,   # deviation from nearest semitone
        }
    """
    if pitch_timeline is None:
        pitch_timeline = []

    # ── Try Groq ─────────────────────────────────────────────────────────
    if GROQ_API_KEY:
        try:
            system_prompt = _SYSTEM[age_group]
            user_prompt   = _build_user_prompt(
                instrument, note, frequency, cents,
                accuracy, consistency, age_group,
                all_notes, pitch_timeline,
            )
            raw    = _call_groq(system_prompt, user_prompt)
            result = _parse_groq_response(
                raw, accuracy, consistency, cents,
                instrument, note, age_group,
            )
            return result

        except requests.exceptions.Timeout:
            print("[feedback] Groq timeout — using local fallback.")
        except requests.exceptions.HTTPError as e:
            print(f"[feedback] Groq HTTP error {e.response.status_code} — using local fallback.")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[feedback] Groq response parse error: {e} — using local fallback.")
        except Exception as e:
            print(f"[feedback] Groq unexpected error: {e} — using local fallback.")

    # ── Local fallback ────────────────────────────────────────────────────
    return _local_fallback(
        instrument, note, frequency, cents,
        accuracy, consistency, age_group, all_notes,
    )