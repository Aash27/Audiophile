import os
import re
from groq import Groq

# ── Config ──────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

print("GROQ_API_KEY LENGTH:", len(GROQ_API_KEY))

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing")

client = Groq(api_key=GROQ_API_KEY)


def grade_from_accuracy(accuracy: float):
    if accuracy >= 90: return "A"
    if accuracy >= 82: return "B+"
    if accuracy >= 74: return "B"
    if accuracy >= 65: return "C+"
    if accuracy >= 55: return "C"
    return "D"


def consistency_label(consistency: float):
    if consistency >= 85: return "Solid"
    if consistency >= 70: return "Fair"
    if consistency >= 55: return "Unstable"
    return "Erratic"


def intonation_label(cents: float):
    if abs(cents) <= 10:
        return "In Tune ✓", "intune"
    elif cents > 0:
        return f"+{cents:.0f}¢ Sharp ♯", "sharp"
    else:
        return f"{cents:.0f}¢ Flat ♭", "flat"


# ── Highlight notes like G#2 ─────────────────────────────
def highlight_notes(text):
    return re.sub(r'\b([A-G]#?\d)\b', r'<b>\1</b>', text)


# ── Tone based on age ───────────────────────────────────
def get_system_prompt(age_group):
    if age_group == "Child (6-12)":
        return "You are a kind music teacher. Keep feedback simple and encouraging."
    elif age_group == "Teen (13-18)":
        return "You are a direct music coach. Be clear and helpful."
    else:
        return "You are a professional music coach. Be precise and concise."


# ── Main Function ───────────────────────────────────────
def generate_feedback(
    instrument,
    note,
    frequency,
    cents,
    accuracy,
    consistency,
    age_group,
    all_notes,
    pitch_timeline=None,
):
    print("USING GROQ")

    system_prompt = get_system_prompt(age_group)

    user_prompt = f"""
Instrument: {instrument}
Note: {note}
Frequency: {frequency} Hz
Deviation: {cents} cents
Accuracy: {accuracy}%
Consistency: {consistency}/100

Give 3 to 5 short feedback points.
Each must be on a new line.
Do NOT use *, -, bullet symbols, or emojis.
Keep it clean and professional.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
        max_tokens=200,
    )

    print("GROQ RESPONSE RECEIVED")

    raw = response.choices[0].message.content.strip()

    # ── Clean lines ─────────────────────────────────────
    lines = []
    for line in raw.split("\n"):
        clean = line.strip()
        clean = re.sub(r'^[\*\-\•\s]+', '', clean)
        clean = re.sub(r'[^\x00-\x7F]+', '', clean)

        if clean:
            lines.append(clean)

    # ── Convert to styled tips ──────────────────────────
    tips = []

    for line in lines:
        formatted_text = highlight_notes(line)

        if "good" in line.lower() or "solid" in line.lower():
            icon = "✓"
            color = "green"
        elif "improve" in line.lower() or "flat" in line.lower() or "sharp" in line.lower():
            icon = "⚠"
            color = "red"
        else:
            icon = "→"
            color = "gold"

        tips.append({
            "icon": icon,
            "color": color,
            "text": formatted_text
        })

    return {
        "overview": lines[0] if lines else "",
        "primary_issue": "",
        "correction_drill": "",
        "encouragement": "",
        "accuracy": accuracy,
        "consistency": consistency,
        "grade": grade_from_accuracy(accuracy),
        "cons_label": consistency_label(consistency),
        "tips": tips
    }
