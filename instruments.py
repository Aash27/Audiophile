"""
instruments.py
Defines valid pitch ranges (Hz) and instrument-specific
correction advice for Audiophile.
"""

INSTRUMENT_RANGES = {
    "Guitar":    (82,   880),
    "Piano":     (27,  4186),
    "Voice":     (80,  1000),
    "Clarinet":  (146, 2100),
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
    "Clarinet": {
        "sharp": [
            "You may try pulling out a little at the barrel or middle joint to "
            "physically extend the clarinet and lower its pitch by a few cents.",
            "While keeping your corners firm, try lowering your jaw or "
            "lowering your tongue position to lower the pitch yourself."
        ],
        "flat": [
            "If your barrel/middle joint is pulled out, try pushing them back "
            "in to increase the pitch by a few cents.",
            "Make sure your corners are firm and your tongue position is not "
            "too low. "
        ], 
        "general": [
            "An older reed may affect your intonation. Break in a new reed "
            "and see if your intonation improves with the new reed.",
            "The range in which you play will also affect your intonation, "
            "try taking your music down/up an octave and see your tendencies in that register."
        ]

    }
}
