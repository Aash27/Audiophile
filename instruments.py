"""
instruments.py
Defines valid pitch ranges (Hz) and instrument-specific
correction advice for Audiophile.
"""

INSTRUMENT_RANGES = {
    "Guitar":    (82, 880),
    "Piano":     (27, 4186),
    "Clarinet":  (147, 1568),
    "Violin":    (196, 2637),
    "Flute":     (262, 2093),
    "Voice":     (80, 1000),
}


# Instrument-specific technique tips per intonation problem
INSTRUMENT_TIPS = {
    "Guitar": {
        "sharp": [
            "You're pressing the string too hard behind the fret — excess pressure bends "
            "the pitch sharp. Use only the force needed to get a clean note.",
            "Check whether your finger is sitting too far from the fret wire. "
            "Close placement requires less pressure and keeps pitch centered.",
        ],
        "flat": [
            "You're not pressing close enough to the fret — the string isn't fully "
            "speaking, which pulls the pitch flat. Move your finger toward the fret wire.",
            "Check that adjacent fingers aren't muting or dragging the string down. "
            "Clean hand position fixes most flat-fret issues.",
        ],
        "general": [
            "Run a chromatic scale on a single string with a tuner. Mark which fret "
            "positions drift and drill those specifically.",
            "Record whole notes slowly. Identify problem positions before increasing tempo.",
        ],
    },
    "Violin": {
        "sharp": [
            "Your first finger is sitting too far back from the nut, shortening the "
            "vibrating length. Shift the hand frame slightly toward the bridge.",
            "Check your thumb — if it's wrapped too far around the neck it collapses "
            "the hand and causes sharp intonation across all fingers.",
        ],
        "flat": [
            "Your finger placement is too close to the nut. Extend the hand frame "
            "fractionally — the pitch will come up.",
            "Low bow pressure creates a diffuse flat tone. Increase arm weight into "
            "the string; don't squeeze with the wrist.",
        ],
        "general": [
            "Practice with an open-string drone. Play stopped notes against an open A "
            "or D — your ear will self-correct faster than any exercise.",
            "Slow scales at 40 bpm, one full beat per note. Your problem positions will "
            "expose themselves immediately.",
        ],
    },
    "Piano": {
        "sharp": [
            "Piano pitch is fixed hardware — a consistent sharp reading means the "
            "instrument needs professional tuning. Verify against A=440 with a tuner app.",
            "If this is a digital piano, check that pitch bend and transpose settings "
            "are both at zero.",
        ],
        "flat": [
            "Same issue as sharp — acoustic piano pitch is not touch-sensitive. "
            "A flat reading is a tuning problem, not a technique problem. Get it tuned.",
            "On digital instruments: confirm the master tuning setting is at 0 cents "
            "and no transpose is engaged.",
        ],
        "general": [
            "Focus on note evenness — record a slow scale and listen for notes that "
            "speak earlier or decay faster. Consistency matters as much as pitch.",
            "If your piano hasn't been tuned in over a year, recording pitch data on it "
            "is wasting practice time. Schedule a tuning first.",
        ],
    },
    "Flute": {
        "sharp": [
            "Your embouchure hole is too open. Roll the head joint in (toward you) — "
            "each degree of roll drops the pitch noticeably.",
            "Air speed is too high. Slow the stream and direct it slightly downward.",
        ],
        "flat": [
            "Roll the head joint out (away from you) to open the embouchure more.",
            "Air pressure is too low. Support the column from the diaphragm — "
            "a thin, unsupported stream always reads flat.",
        ],
        "general": [
            "Mark the in-tune head joint position with a pencil dot so you reset "
            "correctly every session — consistency starts before you play a note.",
            "Long tone and harmonic exercises expose embouchure inconsistency faster "
            "than scale work. Start there.",
        ],
    },
    "Saxophone": {
        "sharp": [
            "You're biting the reed too hard. Jaw pressure closes the reed, raises "
            "pitch. Relax the lower jaw and let the reed vibrate freely.",
            "Check reed strength — a reed too stiff for your embouchure causes chronic "
            "sharpness because you compensate by squeezing.",
        ],
        "flat": [
            "Insufficient air support is the primary cause. Engage the diaphragm — "
            "maintain a full, pressurized column at all times.",
            "Check mouthpiece seating depth. Too far on lowers pitch. Mark the "
            "correct position and reset it every session.",
        ],
        "general": [
            "Long tones on concert Bb, F, and C are your anchor pitches. If those "
            "are off, everything else will be off.",
            "Record yourself on altissimo passages — voicing ('tee' shape) lifts the "
            "pitch center significantly in that register.",
        ],
    },
    "Trumpet": {
        "sharp": [
            "You're overblowing in the middle register. Back off the air stream and "
            "let the embouchure do more work — less air, more focus.",
            "Check that the mouthpiece isn't pushed in too far. A fraction of pull-out "
            "drops the pitch back to center.",
        ],
        "flat": [
            "Insufficient air support, especially in the lower register. Drive more "
            "air column — engage the diaphragm.",
            "Embouchure is too relaxed. Firm the lip corners without clenching, and "
            "direct air forward rather than downward.",
        ],
        "general": [
            "10 minutes of long tones daily, minimum. Sustain each pitch and listen "
            "before checking the tuner. Train the ear first.",
            "Lip slurs between partials build the muscle control that makes intonation "
            "automatic. Clarke Technical Studies are non-negotiable.",
        ],
    },
    "Voice": {
        "sharp": [
            "Tension in the jaw or tongue raises pitch. Drop the jaw, relax the tongue "
            "root, and let the resonance do the work.",
            "Check your breath support — an over-driven air column on light passages "
            "pushes pitch sharp. Match air pressure to dynamic level.",
        ],
        "flat": [
            "Insufficient breath support is the single most common cause of flat "
            "singing. Engage the diaphragm on every phrase, not just high notes.",
            "Lift your soft palate — a low palate drops resonance and pulls pitch flat. "
            "Think of inhaling the sound upward as you sing.",
        ],
        "general": [
            "Record yourself on a single sustained pitch at mp (medium soft). "
            "Listen for drift at the end of the phrase — that's where support fails.",
            "Arpeggios slowly on vowel shapes expose where your registration break "
            "causes pitch inconsistency. Work the passaggio deliberately.",
        ],
    },
}
